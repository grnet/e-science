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
		promise = this.store.fetch('user', 1);
		this.set('promise', promise);
		return promise;
	},
	afterModel : function(data, transition) {
		var that = this;
		this.get('promise').then(function(value) {
			// success
			that.controllerFor('userWelcome').set('sortbystatus', true);
			that.controllerFor('userWelcome').send('timer', true, that.store);
		}, function(reason) {
			// failure
			console.log(String(reason));
		});
	}
});

