// Login route
App.UserLoginRoute = Ember.Route.extend({
	// If user is logged in, redirect to welcome screen
	redirect : function() {
		if (this.controllerFor('user.login').isLoggedIn()) {
			this.transitionTo('user.welcome');
		}
	}
});
