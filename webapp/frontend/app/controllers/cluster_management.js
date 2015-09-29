safestr = Ember.Handlebars.SafeString;
App.ClusterManagementController = Ember.Controller.extend({
	
	needs : ['clusterCreate','helpImages','userWelcome'],
	hue_login_message : '',
	hue_message : '',
    count : 0,
    initial_timer_active : function(){
        return this.get('count')>0;
    }.property('count'),
	orkaImages : [],
    // tabs info for template
    content_tabs_info : {
        info: {id:'id_tab_info',href:'#id_tab_info',name:'Info',active:true},
        access: {id:'id_tab_access',href:'#id_tab_access',name:'Access'},
        manage : {id:'id_tab_manage',href:'#id_tab_manage',name:'Manage'},
        scale : {id:'id_tab_scale',href:'#id_tab_scale',name:'Scale'}
    },
    content_tabs : function(key,value){
        var tabs_object = this.get('content_tabs_info');
        if (arguments.length>1){//setter
            // must use Ember.set() to workaround Ember 1.8.x issue 
            // ref: http://discuss.emberjs.com/t/ember-1-8-you-must-use-ember-set-to-set-the-property/6582, https://github.com/emberjs/ember.js/issues/10209
            Ember.set(tabs_object.info,'active',false);
            Ember.set(tabs_object.access,'active',false);
            Ember.set(tabs_object.manage,'active',false);
            Ember.set(tabs_object.scale,'active',false);
            switch(value) {
            case "info":
                Ember.set(tabs_object.info,'active',true);
                break;
            case "access":
                Ember.set(tabs_object.access,'active',true);
                break;
            case "manage":
                Ember.set(tabs_object.manage,'active',true);
                break;
            case "scale":
                Ember.set(tabs_object.scale,'active',true);
                break;
            }
            this.set('content_tabs_info',tabs_object);
            return tabs_object;
        }
        return tabs_object;
    }.property(),
    state_message : function() {
        var stat_message = this.get('content.state');
        if (!Ember.isBlank(stat_message)) {
            var cluster_name = this.get('content.cluster_name');
            var msg = {
                'msg_type' : 'default',
                'msg_text' : cluster_name +': ' + stat_message
            };
            this.get('controllers.userWelcome').send('addMessage', msg);
        }
    }.observes('content.state'),
	cluster_slaves_newsize_static : null,
	cluster_slaves_newsize : function(key, value){
	    if (arguments.length > 1){//setter
	        this.set('cluster_slaves_newsize_static',value);
	    }
	    return Ember.isEmpty(this.get('cluster_slaves_newsize_static')) ? this.get('content.cluster_slaves_num') : this.get('cluster_slaves_newsize_static'); // getter
	}.property('content.cluster_slaves_num','cluster_slaves_newsize_static'),
	slaves_resize_disabled : function(){
	    var enabled = this.get('content.cluster_status')=='1' && this.get('content.hadoop_status')!='2' && this.get('content.hadoop_status')!='3';
	    return !enabled;
	}.property('content.cluster_status','content.hadoop_status'),
	apply_resize_disabled : function(){
	    return this.get('slaves_resize_disabled') || this.get('cluster_slaves_delta') == 0 || this.get('initial_timer_active');
	}.property('cluster_slaves_delta','slaves_resize_disabled','cluster_slaves_newsize'),
	slaves_increment_disabled : function(){
        if (this.get('slaves_increment_loader')) return true;
        var cluster_project_data = this.get('cluster_project_data');
        if (!Ember.isEmpty(cluster_project_data)){
            var cluster_delta_next = Number(this.get('cluster_slaves_delta'))+1;
            var cpu_request_next = Number(this.get('content.cpu_slaves'))*cluster_delta_next;
            var ram_request_next = Number(this.get('content.ram_slaves'))*cluster_delta_next;
            var disk_request_next = Number(this.get('content.disk_slaves'))*cluster_delta_next;
            var cpu_available = Number(cluster_project_data.get('cpu_av'));
            var ram_available = Number(cluster_project_data.get('ram_av'));
            var disk_available = Number(cluster_project_data.get('disk_av'));
            var vms_available = Number(cluster_project_data.get('vms_av').get("lastObject"));
            return (cluster_delta_next>vms_available) || (cpu_request_next>cpu_available) || (ram_request_next>ram_available) || (disk_request_next>disk_available);
        }
        return false;
	}.property('cluster_slaves_delta','slaves_increment_loader','cluster_project_data'),
	slaves_decrement_disabled : function(){
	    var cluster_min_slaves_allowed = Math.max(1,Number(this.get('content.replication_factor')));
	    return this.get('cluster_slaves_newsize') > cluster_min_slaves_allowed ? false : true;
	}.property('cluster_slaves_newsize'),
	cluster_slaves_delta : function(){
	    return this.get('cluster_slaves_newsize') - this.get('content.cluster_slaves_num');
	}.property('content.cluster_slaves_num','cluster_slaves_newsize'),
	cluster_slaves_delta_decorated : function(){
	    var num_delta = Number(this.get('cluster_slaves_delta'));
	    if (num_delta>0){
	        return new safestr('<span class="text-success">+%@</span>'.fmt(num_delta));
	    }else if (num_delta<0){
	        return new safestr('<span class="text-danger">%@</span'.fmt(num_delta));
	    }else{
	        return new safestr('<b class="glyphicon glyphicon-resize-full"></b>');   
	    }
	}.property('cluster_slaves_delta'),
	cluster_action_destroy_disable : function(){
	    return this.get('content.cluster_action_destroy_disabled') || this.get('initial_timer_active');
	}.property('content.cluster_action_destroy_disabled','initial_timer_active'),

	actions : {
	    increment_size : function(){
	        this.set('cluster_slaves_newsize',this.get('cluster_slaves_newsize')+1);
	        $('#id_number_of_slaves').focus();
	    },
	    decrement_size : function(){
	        this.set('cluster_slaves_newsize',this.get('cluster_slaves_newsize')-1);
	        $('#id_number_of_slaves').focus();
	    },
	    reset_size : function(){
	        this.set('cluster_slaves_newsize',this.get('content.cluster_slaves_num'));
	    },
	    apply_resize : function(){
	        var self = this;
	        var store = this.get('store');
            var model = this.get('content');
	        if (this.get('cluster_slaves_delta')==0){
	            console.log('no changes to apply');
	        }else{
	            var str_delta = this.get('cluster_slaves_delta') > 0 && '+'+this.get('cluster_slaves_delta') || this.get('cluster_slaves_delta');
                var cluster_id = model.get('id');
                var new_size = model.get('cluster_size')+this.get('cluster_slaves_delta');
                // unload cached records
                store.unloadAll('clusterchoice');
                var promise = store.push('clusterchoice',{
                    'id': 1,
                    'cluster_edit': cluster_id,
                    'cluster_size': new_size
                }).save();
                promise.then(function(data){
                    var count = self.get('count');
                    var extend = Math.max(5, count);
                    self.set('count', extend);
                    self.send('timer', true, store);
                },function(reason){
                    console.log(reason.message);
                });
	        }
	    },
		help_hue_login : function(os_image){
			if (/Ecosystem/.test(os_image) || /Hue/.test(os_image)){
				this.set('hue_login_message', '<b>Hue first login</b><br><span class="text text-info">username : hduser</span>');
				this.set('hue_message', 'HUE');
			}else if (/CDH/.test(os_image)){
				this.set('hue_login_message', '<b>Hue first login</b><br><span class="text text-info">username : hdfs</span>');
				this.set('hue_message', 'CDH');
			}else if (/Debian/.test(os_image) || /Hadoop/.test(os_image)){
				this.set('hue_login_message', '');
				this.set('hue_message', '');
			}
			this.get('controllers.clusterCreate').set('hue_message', this.get('hue_message'));
		},
        setActiveTab : function(tab){
            this.set('content_tabs',tab);
        },
		visitActiveImage : function(os_image){
		    for (i=0;i<this.get('orkaImages').length;i++){
		        if (this.get('orkaImages').objectAt(i).get('image_name') == os_image){
		            this.get('controllers.helpImages').send('setActiveImage',this.get('orkaImages').objectAt(i).get('image_pithos_uuid'));
		            this.transitionToRoute('help.images');
		            break;
		        }
		    }
		},
        timer : function(status, store) {
            var that = this;
            if (Ember.isNone(this.get('timer'))) {
                this.set('timer', App.Ticker.create({
                    seconds : 5,
                    onTick : function() {
                        if (!store) {
                            store = that.store;
                        }
                        if (store && that.controllerFor('application').get('loggedIn')) {
                            var promise = store.fetch('user', 1);
                            promise.then(function(user) {
                                // success
                                var user_clusters = user.get('clusters');
                                var num_records = user_clusters.get('length');
                                var model = that.get('content');
                                var cluster_id = model.get('id');
                                var bPending = false;
                                for ( i = 0; i < num_records; i++) {
                                    if ((user_clusters.objectAt(i).get('id') == cluster_id) 
                                    && ((user_clusters.objectAt(i).get('cluster_status') == '2') || (user_clusters.objectAt(i).get('hadoop_status') == '2'))) {
                                        bPending = true;
                                        break;
                                    }
                                }
                                if (!bPending) {
                                    if (that.get('count') > 0) {
                                        that.set('count', that.get('count') - 1);
                                    } else {
                                        that.get('timer').stop();
                                        that.set('count', 0);
                                        status = false;
                                    }
                                }
                            }, function(reason) {
                                that.get('timer').stop();
                                that.set('count', 0);
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
                    that.set('count', 0);
                }
            }
            if (status) {
                this.get('timer').start();
            } else {
                this.get('timer').stop();
                that.set('count', 0);
            }
        },
    }

});