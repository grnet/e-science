App.VreserverManagementController = Ember.Controller.extend({
	
	needs : ['vreserverCreate','helpImages'],
    count : 0,
    orkaImages : [],
	
	actions : {
		
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
                                var user_vreservers = user.get('vreservers');
                                var num_records = user_vreservers.get('length');
                                var model = that.get('content');
                                var vreserver_id = model.get('id');
                                var bPending = false;
                                for ( i = 0; i < num_records; i++) {
                                    if ((user_vreservers.objectAt(i).get('id') == vreserver_id) 
                                    && (user_vreservers.objectAt(i).get('server_status') == '2') ) {
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