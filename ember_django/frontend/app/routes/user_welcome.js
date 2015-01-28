// Welcome user route.
// Show user id, number of clusters and table of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs : 'userWelcome',
	promise : null,

	model : function() {
		$.loader.close(true);
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		var promise = this.store.fetch('user', 1);
		this.set('promise', promise);
		return promise;
	},
	afterModel : function(data, transition) {
		var that = this;
		this.get('promise').then(function(user) {
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
			console.log(String(reason));
		});
	}
});

