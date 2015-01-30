// Welcome user route.
// Show user id, number of clusters and table of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs : 'userWelcome',

	model : function(params, transition) {
		$.loader.close(true);
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		var that = this;
		var promise = this.store.fetch('user', 1);
		promise.then(function(user) {
			// success
			that.controllerFor('userWelcome').set('sortbystatus', true);
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
		var that = this;
		that.controllerFor('userWelcome').set('sortbystatus', true);
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
	},
	deactivate : function() {
		this.controllerFor('userWelcome').send('timer', false);
	},
});

