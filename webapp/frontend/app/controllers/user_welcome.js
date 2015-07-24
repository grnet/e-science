// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

    needs : ['clusterCreate','vreserverCreate'],
    orkaImages: [],
    vreImages: [],
    user_messages : [],
    // blacklist user messages explicitly removed during polling
    blacklist_messages : {},
    // flag to denote transition from create cluster button
    create_cluster_start : false,
    count : 0,
    master_vm_password_msg : function() {
        var pwd_message = this.get('content.master_vm_password');
        if (!Ember.isBlank(pwd_message)) {
            var msg = {
                'msg_type' : 'warning',
                'msg_text' : pwd_message
            };
            this.send('addMessage', msg);
        }
    }.observes('content.master_vm_password'),
    error_message : function() {
        var err_message = this.get('content.error_message');
        if (!Ember.isBlank(err_message)) {
            var msg = {
                'msg_type' : 'danger',
                'msg_text' : err_message
            };
            this.send('addMessage', msg);
        }
    }.observes('content.error_message'),
    no_messages : function() {
        var num_messages = Number(this.get('user_messages').get('length'));
        return (num_messages == 0 || Ember.isEmpty(num_messages));
    }.property('user_messages.@each'),
    get_sorting_info : function(short_model_name, sortdir, column){
        var last_sort = '%@_%@'.fmt(short_model_name,column);
        var prop_arrow_show = '%@_%@_show'.fmt(short_model_name,column);
        var prop_arrow_dir = '%@_%@_dir'.fmt(short_model_name,column);
        var obj = {};
        obj[prop_arrow_show] = true;
        obj[prop_arrow_dir] = sortdir;
        obj.last_sort = column;
        return {'sorting_info': obj};
    },
    actions : {
        sortBy2 : function(model, column){
            model.set('sortProperties',[column]);
            model.set('sortAscending', !model.get('sortAscending'));
            this.setProperties(this.get_sorting_info(model.get('short_model_name'),model.get('sortAscending'),column));
        },
        addMessage : function(obj) {
            // routes/controllers > controller.send('addMessage',{'msg_type':'default|info|success|warning|danger', 'msg_text':'Lorem ipsum dolor sit amet, consectetur adipisicing elit'})
            // templates > {{#each message in user_messages}}{{message.msg_text}}{{/each}}
            var self = this;
            var store = this.store;
            var messages = store.all('usermessages');
            var aryMessages = messages.toArray();
            var count = messages.get('length') || 0;
            var aryBlacklist = self.get('blacklist_messages');
            var bBlacklist_or_Dupe = false;
            var inc_message = String(obj['msg_text']);
            $.each(aryMessages, function(i, message) {
                var old_message = message.get('msg_text');
                if (inc_message == old_message) {
                    bBlacklist_or_Dupe = true;
                    return false;
                }
            });
            if (aryBlacklist[inc_message]) {
                bBlacklist_or_Dupe = true;
            }
            if (!bBlacklist_or_Dupe) {
                // cap at 10 items for now
                if (count > 9) {
                    var record = messages.get('firstObject');
                    if (!Ember.isEmpty(record)) {
                        store.deleteRecord(record);
                        messages.compact();
                    }
                }
                var message = {
                    msg_type : obj['msg_type'],
                    msg_text : inc_message
                };
                while (store.hasRecordForId('usermessages', count)) {
                    count += 1;
                }
                message['id'] = count;
                store.createRecord('usermessages', message);
                this.set('user_messages', messages);
            }
        },
        removeMessage : function(id, all) {
            // routes/controllers > controller.send('removeMessage', id, [all=false]) optional 3rd parameter to true will clear all messages
            // templates > {{action 'removeMessage' message_id}} / {{action 'removeMessage' 1 true}}
            var self = this;
            var store = this.store;
            var messages = store.all('usermessages');
            var aryMessages = messages.toArray();
            var count = messages.get('length') || 0;
            var aryBlacklist = self.get('blacklist_messages');
            if (all === true) {
                $.each(aryMessages, function(i, message) {
                    var old_message = message.get('msg_text');
                    aryBlacklist[old_message] = true;
                });
                store.unloadAll('usermessages');
                messages.compact();
            } else {
                var record = store.getById('usermessages', id);
                if (!Ember.isEmpty(record)) {
                    var message = String(record.get('msg_text'));
                    aryBlacklist[message] = true;
                    store.deleteRecord(record);
                    messages.compact();
                }
            }
            this.set('user_messages', messages);
        },
        timer : function(status, store) {
            var that = this;
            if (Ember.isNone(this.get('timer'))) {
                this.set('timer', App.Ticker.create({
                    seconds : 5,
                    onTick : function() {
                        that.set('create_cluster_start', false);
                        if (!store) {
                            store = that.store;
                        }
                        if (store && that.controllerFor('application').get('loggedIn')) {
                            var promise = store.fetch('user', 1);
                            promise.then(function(user) {
                                // success
                                var user_clusters = user.get('clusters');
                                var num_cluster_records = user_clusters.get('length');
                                var user_vreservers = user.get('vreservers');
                                var num_vre_records = user_vreservers.get('length');
                                var bPending = false;
                                for ( i = 0; i < num_cluster_records; i++) {
                                    if ((user_clusters.objectAt(i).get('cluster_status') == '2') || (user_clusters.objectAt(i).get('hadoop_status') == '2')) {
                                        bPending = true;
                                        // TODO: sort
                                        break;
                                    }
                                }
                                for ( i = 0; i < num_vre_records; i++ ) {
                                    if (user_vreservers.objectAt(i).get('server_status') == '2'){
                                        bPending = true;
                                        // TODO: sort
                                        break;
                                    }
                                }
                                if (!bPending) {
                                    if (that.get('count') > 0) {
                                        that.set('count', that.get('count') - 1);
                                    } else {
                                        that.get('timer').stop();
                                        status = false;
                                    }
                                }
                            }, function(reason) {
                                that.get('timer').stop();
                                status = false;
                                console.log(reason.message);
                            });
                            return promise;
                        }
                    }
                }));
            } else {
                if (status) {
                    that.get('timer').start();
                } else {
                    that.get('timer').stop();
                }
            }
            if (status) {
                this.get('timer').start();
            } else {
                this.get('timer').stop();
            }
        },
    }
});
