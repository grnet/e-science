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
		
		takeDslAction : function(experiment) {
			var self = this;
            var store = this.store;
		},
		confirmDslAction : function(experiment, value) {
            experiment.set('action_dsl_confirm', value);
		}	
	},
	deactivate : function() {
        // left this route
    }
	  
});