// Index route (e.g localhost:port/) redirects to homepage
App.IndexRoute = Ember.Route.extend({
    // redirect
    redirect : function() {
	this.transitionTo('homepage');
    }
});
