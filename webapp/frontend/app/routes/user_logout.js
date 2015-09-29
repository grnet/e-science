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
		var current_user = this.store.push('user', {
			'id' : 1,
            'user_theme' : ''
		}).save();
		current_user.then(function() {
			// Set global var escience and sessionStorage token to null when put is successful.
			App.set('escience_token', "null");
			window.sessionStorage.escience_auth_token = App.get('escience_token');
		}, function(reason) {
			// Set global var escience and sessionStorage token to null when put fails.
			App.set('escience_token', "null");
			window.sessionStorage.escience_auth_token = App.get('escience_token');
			console.log(reason.message);
		});
		// scroll to top of the page
		window.scrollTo(0,0);
		this.transitionTo('homepage');
		this.controllerFor('application').set('loggedIn', false);
		$.loader.close(true);
		this.controllerFor('user.login').cancelRunTimer();
	}
});

	
