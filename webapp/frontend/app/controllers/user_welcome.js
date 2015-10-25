// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

    needs : ['application', 'clusterCreate','vreserverCreate','clusterManagement','dslCreate'],
    // flag to denote transition from a create action
    create_cluster_start : false,
    count : 0,
    initial_timer_active : function(){
        return this.get('count')>0;
    }.property('count'),    
    orkaImages: [],
    vreImages: [],
    user_messages : [],
    // blacklist user messages explicitly removed during polling
    blacklist_messages : {},
    // tabs info for template
    content_tabs_info : {
        clusters: {id:'id_userclusters_tab',href:'#id_userclusters_tab',name:'Hadoop Clusters',active:true},
        vreservers: {id:'id_uservres_tab',href:'#id_uservres_tab',name:'Virtual Research Environments'},
        dsls: {id:'id_userdsls_tab',href:'#id_userdsls_tab',name:'Reproducible Experiments'}
    },
    content_tabs : function(key,value){
        var tabs_object = this.get('content_tabs_info');
        if (arguments.length>1){//setter
            // must use Ember.set() to workaround Ember 1.8.x issue 
            // ref: http://discuss.emberjs.com/t/ember-1-8-you-must-use-ember-set-to-set-the-property/6582, https://github.com/emberjs/ember.js/issues/10209
            Ember.set(tabs_object.vreservers,'active',false);
            Ember.set(tabs_object.clusters,'active',false);
            Ember.set(tabs_object.dsls,'active',false);
            switch(value) {
            case "clusters":
                Ember.set(tabs_object.clusters,'active',true);
                break;
            case "vreservers":
                Ember.set(tabs_object.vreservers,'active',true);
                break;
            case "dsls":
                Ember.set(tabs_object.dsls,'active',true);
                break;
            }
            this.set('content_tabs_info',tabs_object);
            return tabs_object;
        }
        return tabs_object;
    }.property(),
    // userclusters block
    filtered_clusters : function(){
        var clusters = this.get('content.clusters').filterBy('id');
        return this.get('cluster_active_filter') ? clusters.filterBy('cluster_status_active_pending') : clusters;
    }.property('content.clusters.[]','content.clusters.isLoaded','cluster_active_filter'),
    sorted_clusters_prop : ['resorted_status:asc','action_date:desc'],
    sorted_clusters_dir : true,
    sorted_clusters : Ember.computed.sort('filtered_clusters','sorted_clusters_prop'),
    sortable_clusters : function(){
        return this.get('sorted_clusters');
    }.property('filtered_clusters.[]'),
    failed_clusters : function(){
        var clusters = this.get('content.clusters').filterBy('id');
        return clusters.filterBy('cluster_status_verbose','FAILED');
    }.property('content.clusters.[]','content.clusters.isLoaded'),
    boolean_no_failed_clusters : function(){
        var failed_clusters = this.get('failed_clusters');
        return Ember.isEmpty(failed_clusters) || failed_clusters.get('length') == 0; 
    }.property('failed_clusters.[]'),
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
    // userdsls block
    filtered_dsls : function(){
        return this.get('content.dsls').filterBy('id');
    }.property('content.dsls.[]','content.dsls.isLoaded'),
    sorted_dsls_prop : ['resorted_status:asc','action_date:desc'],
    sorted_dsls_dir : true,
    sorted_dsls : Ember.computed.sort('filtered_dsls','sorted_dsls_prop'),
    sortable_dsls : function(){
        return this.get('sorted_dsls');
    }.property('filtered_dsls.[]'),
    // messages / feedback
    dsl_replay_msg : function(self,key){
        var replaying_dsls = self.get('sortable_dsls').filterBy('dsl_status','1');
        for (i=0; i<replaying_dsls.get('length'); i++){
            if (!Ember.isEmpty(replaying_dsls.objectAt(i).get('message_dsl_status_replay'))){
                var msg = {'msg_type':'default','msg_text': replaying_dsls.objectAt(i).get('message_dsl_status_replay')};
                self.send('addMessage',msg);
            }
        }
    }.observes('sortable_dsls.@each.state'),
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
                break;
            case "uv":
                this.set('sorted_vreservers_dir',!this.get('sorted_vreservers_dir'));
                sortAscending = this.get('sorted_vreservers_dir');
                var primarysort = '%@:%@'.fmt(column,sortAscending && 'asc' || 'desc');
                var sort_properties = (column == 'action_date') && [primarysort] || [primarysort,'action_date:desc'];
                this.set('sorted_vreservers_prop',sort_properties);
                break;
            case "ud":
                this.set('sorted_dsls_dir',!this.get('sorted_dsls_dir'));
                sortAscending = this.get('sorted_dsls_dir');
                var primarysort = '%@:%@'.fmt(column,sortAscending && 'asc' || 'desc');
                var sort_properties = (column == 'action_date') && [primarysort] || [primarysort,'action_date:desc'];
                this.set('sorted_dsls_prop',sort_properties);
                break;
            }
            this.setProperties(this.get_sorting_info(short_model_name,sortAscending,column));
        },
        goto_dsl_create : function(cluster){
            this.get('controllers.dslCreate').set('user_clusters',this.get('filtered_clusters'));
            this.get('controllers.dslCreate').send('set_selected_cluster',cluster.get('id'));
            this.transitionToRoute('dsl.create');
        },
        goto_cluster_scale : function(cluster_id){
            this.get('controllers.clusterManagement').send('setActiveTab','scale');
            this.transitionToRoute('cluster.management',cluster_id);
        },
        visit_vreserver_base_url : function(vreserver){
            var os_image = vreserver.get('os_image');
            var server_ip = vreserver.get('server_IP');
            var vreImages = this.get('vreImages');
            var arrAccessUrls = [];
            var base_url = null;
            for (i=0;i<vreImages.length;i++){
                if (vreImages[i].get('image_name') == os_image){
                    var arrImageUrls = vreImages[i].get('image_access_url') || [];
                    for (j=0;j<arrImageUrls.length;j++){
                        arrAccessUrls.push('http://%@:%@'.fmt(server_ip,arrImageUrls[j]));
                    }
                    base_url = (Ember.isEmpty(arrAccessUrls) ? ['http://%@'.fmt(server_ip)] : arrAccessUrls)[0];
                    break;
                }
            }
            if (!Ember.isEmpty(base_url)){
                window.open(base_url,'_blank');
            }        
        },
        setActiveTab : function(tab){
            this.set('content_tabs',tab);  
        },
        setActiveFilter : function(val){
            this.set('cluster_active_filter',val);  
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
            // routes/controllers > controller.send('removeMessage', id, [all=false] all=true > clear all
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
        dismiss : function(){
            $('#id_alert_welcome > button').click();  
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
                        if (store && that.get('controllers.application').get('loggedIn')) {
                            var promise = store.fetch('user', 1);
                            promise.then(function(user) {
                                // success
                                var user_clusters = user.get('clusters');
                                var num_cluster_records = user_clusters.get('length');
                                var user_vreservers = user.get('vreservers');
                                var num_vre_records = user_vreservers.get('length');
                                var user_dsls = user.get('dsls');
                                var num_dsl_records = user_dsls.get('length');
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
                                for ( i = 0; i < num_dsl_records; i++ ) {
                                    if (user_dsls.objectAt(i).get('dsl_status') == '1'){
                                        bPending = true;
                                        break;
                                    }
                                }
                                if (!bPending) {
                                    if (that.get('count') > 0) {
                                        that.set('count', that.get('count') - 1);
                                    } else {
                                        that.get('timer').stop();
                                        that.set('count',0);
                                        status = false;
                                    }
                                }
                            }, function(reason) {
                                that.get('timer').stop();
                                that.set('count',0);
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
                    that.set('count',0);
                }
            }
            if (status) {
                this.get('timer').start();
            } else {
                this.get('timer').stop();
                this.set('count',0);
            }
        },
    }
});
