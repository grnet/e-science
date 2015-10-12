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
    
    // computed properties
    vre_faq_links : function(){
        var os_image = this.get('content.os_image');
        var vreImages = this.get('vreImages');
        for (i=0;i<vreImages.length;i++){
            if (vreImages[i].get('image_name') == os_image){
                return vreImages[i].get('image_faq_links');
            }
        }
    }.property('content.os_image'),
    vre_access_url : function(){
        var os_image = this.get('content.os_image');
        var server_ip = this.get('content.server_IP');
        var vreImages = this.get('vreImages');
        var arrAccessUrls = [];
        for (i=0;i<vreImages.length;i++){
            if (vreImages[i].get('image_name') == os_image){
                var arrImageUrls = vreImages[i].get('image_access_url') || [];
                for (j=0;j<arrImageUrls.length;j++){
                    arrAccessUrls.push('http://%@:%@'.fmt(server_ip,arrImageUrls[j]));
                }
                return Ember.isEmpty(arrAccessUrls) ? ['http://%@'.fmt(server_ip)] : arrAccessUrls;
            }
        }
    }.property('content.server_IP','content.os_image'),
    vre_access_base_url : function(){
        return this.get('vre_access_url')[0];
    }.property('vre_access_url'),
    	
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