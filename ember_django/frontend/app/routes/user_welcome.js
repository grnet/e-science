// Welcome user route.
// Show user id, number of clusters and table of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs : 'userWelcome',

	refreshed : 0,
	model : function(params, transition) {
		$.loader.close(true);
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		var that = this;
		var promise = this.store.fetch('user', 1);
		promise.then(function(user) {
			// success
			var num_records = user.get('clusters').get('length');
			var bPending = false;
			for ( i = 0; i < num_records; i++) {
				if (user.get('clusters').objectAt(i).get('cluster_status') == '2') {
					that.controllerFor('userWelcome').send('timer', true, that.store);
					bPending = true;
					break;
				}
			}
			if (!bPending) {
				that.controllerFor('userWelcome').send('timer', false);
			}
		}, function(reason) {
			// failure
			console.log(reason.message);
		});
		return promise;
	},
	afterModel : function(user, transition) {
		// if we came from a link-to helper that doesn't fire the model hook
		// console.log(user.get('clusters').get('length'));
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'cluster_name');
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'cluster_name');
	},	
	actions : {
		willTransition : function(transition) {
			// leaving this route
			this.controller.send('timer', false);
		},
		didTransition : function() {
			// arrived at this route
			var from_create = this.controller.get('create_cluster_start');
			var times_refreshed = this.get('refreshed');
			if (from_create && (times_refreshed <= 5)) {
				// this.controller.set('create_cluster_start', false);
				Ember.run.later(this, function() {
					// console.log('route > debouncing refresh');
					this.set('refreshed',this.get('refreshed')+1);
					this.controller.send('doRefresh');
				}, 3000);
			}else if (!from_create){
				this.set('refreshed',0);
			}
			return true;
		},
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	},
});

