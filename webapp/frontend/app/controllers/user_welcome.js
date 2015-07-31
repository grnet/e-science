// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

    needs : ['clusterCreate','vreserverCreate'],
    // flag to denote transition from a create action
    create_cluster_start : false,
    count : 0,
    orkaImages: [],
    vreImages: [],
    user_messages : [],
    // blacklist user messages explicitly removed during polling
    blacklist_messages : {},
    // tabs info for template
    content_tabs : function(key,value){
        var tabs_object = {
            clusters: {id:'id_userclusters_tab',href:'#id_userclusters_tab',name:'User Clusters',active:true},
            vreservers: {id:'id_uservres_tab',href:'#id_uservres_tab',name:'User VREs'}};
        if (arguments.length>1){//setter
            switch(value) {
            case "clusters":
                tabs_object["clusters"]["active"]=true;
                tabs_object["vreservers"]["active"]=null;
            case "vreservers":
                tabs_object["vreservers"]["active"]=true;
                tabs_object["clusters"]["active"]=null;
            }
            return tabs_object;
        }
        return tabs_object;
    }.property(),
    // userclusters block
    filtered_clusters : function(){
        return this.get('content.clusters').filterBy('id');
    }.property('content.clusters.[]','content.clusters.isLoaded'),
    sorted_clusters_prop : ['resorted_status:asc','action_date:desc'],
    sorted_clusters_dir : true,
    sorted_clusters : Ember.computed.sort('filtered_clusters','sorted_clusters_prop'),
    sortable_clusters : function(){
        return this.get('sorted_clusters');
    }.property('filtered_clusters.[]'),
    // uservreservers block
    filtered_vreservers : function(){
        return this.get('content.vreservers').filterBy('id');
    }.property('content.vreservers.[]','content.vreservers.isLoaded'),
    sorted_vreservers_prop : ['resorted_status:asc','action_date:desc'],
    sorted_vreservers_dir : true,
    sorted_vreservers : Ember.computed.sort('filtered_vreservers','sorted_vreservers_prop'),
    sortable_vreservers : function(){
        return this.get('sorted_vreservers');
    }.property('filtered_vreservers.[]'),
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
    // utility function. we use it to create dynamic properties for storing on the controller to reference in templates 
    // (eg. "<short_name>_<column_name>_show" on a template will automatically have the correct boolean value to show/hide a sorting arrow)
    get_sorting_info : function(short_model_name, sortdir, column){
        var prop_arrow_show = '%@_%@_show'.fmt(short_model_name,column);
        var prop_arrow_dir = '%@_%@_dir'.fmt(short_model_name,column);
        var obj = {};
        obj[prop_arrow_show] = true;
        obj[prop_arrow_dir] = sortdir;
        obj.last_sort = column;
        obj.last_sort_dir = sortdir;
        obj.last_sort_model = short_model_name;
        return {'sorting_info': obj};
    },
    actions : {
        sortBy : function(model, short_model_name, column){
            var sortAscending = null;
            switch(short_model_name){
            case "uc":
                this.set('sorted_clusters_dir',!this.get('sorted_clusters_dir'));
                sortAscending = this.get('sorted_clusters_dir');
                var primarysort = '%@:%@'.fmt(column,sortAscending && 'asc' || 'desc');
                var sort_properties = (column == 'action_date') && [primarysort] || [primarysort,'action_date:desc'];
                this.set('sorted_clusters_prop',sort_properties);
            case "uv":
                this.set('sorted_vreservers_dir',!this.get('sorted_vreservers_dir'));
                sortAscending = this.get('sorted_vreservers_dir');
                var primarysort = '%@:%@'.fmt(column,sortAscending && 'asc' || 'desc');
                var sort_properties = (column == 'action_date') && [primarysort] || [primarysort,'action_date:desc'];
                this.set('sorted_vreservers_prop',sort_properties);
            }
            this.setProperties(this.get_sorting_info(short_model_name,sortAscending,column));
        },
        setActiveTab : function(tab){
            this.set('content_tabs',tab);  
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
                                        break;
                                    }
                                }
                                for ( i = 0; i < num_vre_records; i++ ) {
                                    if (user_vreservers.objectAt(i).get('server_status') == '2'){
                                        bPending = true;
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
