// Index route (e.g localhost:port/)
App.IndexRoute = Ember.Route.extend({
	// redirects to homepage
	redirect : function() {
		this.transitionTo('homepage');
	}
});
