// Welcome functionality
// Welcome user route.
// Show user id and clusters number.
App.UserWelcomeRoute = App.RestrictedRoute.extend({

	model : function() {
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		return this.store.find('user', 1);
	}
});
