App.VreserverManagementController = Ember.Controller.extend({
	
	needs : ['vreserverCreate','helpVreimages'],
    count : 0,
    vreImages : [],
    // tabs info for template
    content_tabs_info : {
        info: {id:'id_tab_info',href:'#id_tab_info',name:'Info',active:true},
        access: {id:'id_tab_access',href:'#id_tab_access',name:'Access'},
        manage : {id:'id_tab_manage',href:'#id_tab_manage',name:'Manage'}
    },
    content_tabs : function(key,value){
        var tabs_object = this.get('content_tabs_info');
        if (arguments.length>1){//setter
            tabs_object["info"]["active"]=false;
            tabs_object["access"]["active"]=false;
            tabs_object["manage"]["active"]=false;
            switch(value) {
            case "info":
                tabs_object["info"]["active"]=true;
                break;
            case "access":
                tabs_object["access"]["active"]=true;
                break;
            case "manage":
                tabs_object["manage"]["active"]=true;
                break;
            }
            this.set('content_tabs_info',tabs_object);
            return tabs_object;
        }
        return tabs_object;
    }.property(),
    	
	actions : {
        setActiveTab : function(tab){
            this.set('content_tabs',tab);  
        },		
		
		visitActiveImage : function(os_image){
		    for (i=0;i<this.get('vreImages').length;i++){
		        if (this.get('vreImages').objectAt(i).get('image_name') == os_image){
		            this.get('controllers.helpVreimages').send('setActiveImage',this.get('vreImages').objectAt(i).get('image_pithos_uuid'));
		            this.transitionToRoute('help.vreimages');
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