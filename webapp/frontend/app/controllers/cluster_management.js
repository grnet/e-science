safestr = Ember.Handlebars.SafeString;
App.ClusterManagementController = Ember.Controller.extend({
	
	needs : ['clusterCreate','helpImages'],
	hue_login_message : '',
	hue_message : '',
    count : 0,
	orkaImages : [],
    // tabs info for template
    content_tabs_info : {
        info: {id:'id_tab_info',href:'#id_tab_info',name:'Info',active:true},
        access: {id:'id_tab_access',href:'#id_tab_access',name:'Access'},
        manage : {id:'id_tab_manage',href:'#id_tab_manage',name:'Manage'}
    },
    content_tabs : function(key,value){
        var tabs_object = this.get('content_tabs_info');
        if (arguments.length>1){//setter
            // must use Ember.set() to workaround Ember 1.8.x issue 
            // ref: http://discuss.emberjs.com/t/ember-1-8-you-must-use-ember-set-to-set-the-property/6582, https://github.com/emberjs/ember.js/issues/10209
            Ember.set(tabs_object.info,'active',false);
            Ember.set(tabs_object.access,'active',false);
            Ember.set(tabs_object.manage,'active',false);
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
            }
            this.set('content_tabs_info',tabs_object);
            return tabs_object;
        }
        return tabs_object;
    }.property(),	
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
	    return this.get('slaves_resize_disabled') || this.get('cluster_slaves_delta') == 0;
	}.property('cluster_slaves_delta','slaves_resize_disabled'),
	slaves_increment_disabled : function(){
	    // TODO arithmetic with slave config and available resources (cpu,ram,disk etc)
	    return false;
	}.property('cluster_slaves_newsize'),
	slaves_decrement_disabled : function(){
	    return this.get('cluster_slaves_newsize') > 1 ? false : true;
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
	        if (this.get('cluster_slaves_delta')==0){
	            console.log('no changes to apply');
	        }else{
	            var str_delta = this.get('cluster_slaves_delta') > 0 && '+'+this.get('cluster_slaves_delta') || this.get('cluster_slaves_delta');
	            console.log('apply scale: ' + str_delta);
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