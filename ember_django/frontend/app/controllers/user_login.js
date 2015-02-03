// Login controller
App.UserLoginController = Ember.Controller.extend({
	needs: 'application',
	token : '',
	isLoggedIn : function() {
		// Check local storage auth token for user login status.
		if (window.localStorage.escience_auth_token != 'null' && !Ember.isEmpty(window.localStorage.escience_auth_token) && window.localStorage.escience_auth_token !== 'undefined') {
			this.set('controllers.application.loggedIn', true);
			return true;
		} else {
			this.set('controllers.application.loggedIn', false);
			return false;
		}
	},
	loginFailed : false,
	actions : {		
		login : function(text) {
			var self = this;
			if (text) {
				// POST ~okeanos token to Django backend.
				var response = this.store.createRecord('user', {
					'token' : text
				}).save();
				// Handling the promise of POST request
				response.then(function(data) {
					// Succesfull login.
					// Set global and localStorage variables to escience token.
					App.set('escience_token', "Token " + data._data.escience_token);
					window.localStorage.escience_auth_token = App.get('escience_token');
					// Push to store the user retrieved from Django backend.
					self.store.push('user', {
						id : 1,
						user_id : data._data.user_id,
						token : data._data.escience_token,
						user_theme : data._data.user_theme,
						cluster : data._data.cluster
					});
					// Set the text in login screen to blank and redirect to welcome screen
					self.set('loginFailed', false);
					self.set('controllers.application.loggedIn', true);
					self.set('token', '');
					self.transitionToRoute('user.welcome');
				}, function() {
					// Failed login.
					self.set('loginFailed', true);
					self.set('controllers.application.loggedIn', false);
					self.set('token', '');
				});

			}
		}
	}
}); 