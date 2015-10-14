App.DslManagementRoute = App.RestrictedRoute.extend({

	// model for Experiments management route
	needs: ['dslManagement','userWelcome'],
	model: function(params, transition) {

		var that = this;
		// find the correct experiment
		var promise = this.store.fetch('user', 1).then(function(user) {
	
			// find all experiments of user
			var experiments = user.get('dsls');
			var length = experiments.get('length');
			if (length > 0) {
			    var bPending = false;
				for (var i = 0; i < length; i++) {
					// check for the experiment id
					if (experiments.objectAt(i).get('id') == params["dsl.id"])
					{
					    var this_experiment = experiments.objectAt(i);
					 	return this_experiment;
					}
				}
			}
 		}, function(reason) {
			console.log(reason.message);
		});
	 	return promise;
	},
	
	// possible actions
	actions: {
	    willTransition : function(transition) {
            // leaving this route
        },
		didTransition : function(){
		    // entered this route
		},
		takeDslAction : function(dsl) {
			var self = this;
            var store = this.store;
            var action = dsl.get('action_dsl_confirm');
            dsl.set('action_dsl_confirm', false);
            switch(action) {
            case 'dsl_delete':
                dsl.destroyRecord().then(function(data) {
                    var count = self.controller.get('count');
                    var extend = Math.max(5, count);
                    self.controller.set('count', extend);
                    self.controllerFor('userWelcome').set('create_cluster_start', true);
                    self.controllerFor('userWelcome').send('timer', true, store);
                    self.controllerFor('userWelcome').send('setActiveTab','dsls');
                    self.transitionTo('user.welcome');
                }, function(reason) {
                    console.log(reason.message);
                    if (!Ember.isBlank(reason.message)){
                        var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controllerFor('userWelcome').send('addMessage',msg);
                    }
                });
                break;
            case 'dsl_replay':
                dsl.save().then(function(data){
                    console.log('update');
                },function(reason){
                    if (!Ember.isBlank(reason.message)){
                        var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controllerFor('userWelcome').send('addMessage',msg);
                    }
                });
            }
		},
		confirmDslAction : function(dsl, value) {
            dsl.set('action_dsl_confirm', value);
		}	
	},
	deactivate : function() {
        // left this route
    }
	  
});