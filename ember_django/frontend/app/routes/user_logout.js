// Logout route (Log out user).
App.UserLogoutRoute = Ember.Route.extend({
	needs: 'clusterCreate',
	// redirect accordingly
	redirect : function() {
		// clear data store cache for 'cluster'
		this.store.unloadAll('cluster');
		// reset variables in create cluster
		this.controllerFor('clusterCreate').reset_variables();
		// reset variables in create cluster
		this.controllerFor('clusterCreate').reset_project();
		// Send PUT request for backend logout update.
		var current_user = this.store.update('user', {
			'id' : 1
		}).save();
		current_user.then(function() {
			// Set global var escience and localStorage token to null when put is successful.
			App.set('escience_token', "null");
			window.localStorage.escience_auth_token = App.get('escience_token');
		}, function() {
			// Set global var escience and localStorage token to null when put fails.
			App.set('escience_token', "null");
			window.localStorage.escience_auth_token = App.get('escience_token');
		});
		this.transitionTo('homepage');
		this.controllerFor('application').set('loggedIn', false);
	}
});
