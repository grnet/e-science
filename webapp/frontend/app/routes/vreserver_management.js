App.VreserverManagementRoute = App.RestrictedRoute.extend({

	// model for VRE server management route
	needs: ['vreserverManagement','userWelcome'],
	model: function(params, transition) {

		var that = this;
		// find the correct cluster
		var promise = this.store.fetch('user', 1).then(function(user) {
	
			// find all clusters of user
			var vreservers = user.get('vreservers');
			var length = vreservers.get('length');
			if (length > 0) {
			    var bPending = false;
				for (var i = 0; i < length; i++) {
					// check for the server id
					if (vreservers.objectAt(i).get('id') == params["vreserver.id"])
					{
					    var this_vreserver = vreservers.objectAt(i);
						
                        if (this_vreserver.get('server_status') == '2') {
                            that.controllerFor('vreserverManagement').send('timer', true, that.store);
                            bPending = true;
                        }else{
                            that.controllerFor('vreserverManagement').send('timer',false);
                        }
					 	return this_vreserver;
					}
				}
				if (!bPending){
				    that.controllerFor('vreserverManagement').send('timer',false);
				}
			}
	
 		}, function(reason) {
			console.log(reason.message);
			that.controllerFor('vreserverManagement').send('timer',false);
		});
	 	return promise;
	},
	
	// possible actions
	actions: {
	    willTransition : function(transition) {
            // leaving this route
            this.controller.send('timer', false);
        },
		
		takeAction : function(vreserver) {
			var self = this;
			var store = this.store;
			var action = vreserver.get('cluster_confirm_action');
			vreserver.set('cluster_confirm_action', false);
			switch(action) {
			case 'server_delete':
				vreserver.destroyRecord().then(function(data) {
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.send('timer', true, store);
				}, function(reason) {
					console.log(reason.message);
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controllerFor('userWelcome').send('addMessage',msg);
					}
				});
				break;
			}
		},
		
		confirmAction : function(vreserver, value) {
			vreserver.set('cluster_confirm_action', value);
		}	
	},
	deactivate : function() {
        // left this route
        this.controller.send('timer', false);
    }
	  
});