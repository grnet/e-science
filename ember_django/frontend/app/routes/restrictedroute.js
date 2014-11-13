// Every route that requires loggedIn user will extend this route
App.RestrictedRoute = Ember.Route.extend({
	beforeModel : function() {
		// Check if user is logged in.
		// If not, redirect to login screen.
		if (!this.controllerFor('user.login').isLoggedIn()) {
			this.transitionTo('user.login');
		} else {
			// set auth_token to global variable
			App.set('escience_token', window.localStorage.escience_auth_token);
		}
	}
});
