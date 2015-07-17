App.ClusterManagementController = Ember.Controller.extend({
	
	needs : ['clusterCreate','helpImages'],
	hue_login_message : '',
	hue_message : '',
    count : 0,
	orkaImages : [],
	
	actions : {
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