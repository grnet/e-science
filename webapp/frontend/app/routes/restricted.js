// Every route that requires loggedIn user will extend this route
App.RestrictedRoute = Ember.Route.extend({
	beforeModel : function(transition) {
		// Check if user is logged in.
		// If not, redirect to login page.
		if (!this.controllerFor('user.login').isLoggedIn()) {
			// store the transition the user attempted, to retry after login
			this.controllerFor('user.login').set('previousTransition', transition);
			this.transitionTo('user.login');
		} else {
			// set auth_token to global variable
			App.set('escience_token', window.sessionStorage.escience_auth_token);
			this.controllerFor('user.login').runTimer();
		}
	}
});
