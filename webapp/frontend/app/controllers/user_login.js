// Login controller
App.UserLoginController = Ember.Controller.extend({
	needs: 'application',
	token : '',
	runLater : null,
	okeanos_api_url : 'https://astakos.okeanos-knossos.grnet.gr/ui/api_access',
	logout_time_limit : 7200000, //time in milliseconds after which user will be logged out
	isLoggedIn : function() {
		// Check local storage auth token for user login status.
		if (window.sessionStorage.escience_auth_token != 'null' && !Ember.isEmpty(window.sessionStorage.escience_auth_token) && window.sessionStorage.escience_auth_token !== 'undefined') {
			this.set('controllers.application.loggedIn', true);
			return true;
		} else {
			this.set('controllers.application.loggedIn', false);
			return false;
		}
	},
	loginFailed : false,
	actions : {
		// action login, reads input text
		login : function(text) {
			var self = this;
			if (text) {
				text = $.trim(text);
				// POST ~okeanos token to Django backend.
				var response = this.store.createRecord('user', {
					'token' : text
				}).save();
				// Handling the promise of POST request
				response.then(function(user) {
					// Succesfull login.
					// Set global and sessionStorage variables to escience token.
					App.set('escience_token', "Token " + user.get('escience_token'));
					window.sessionStorage.escience_auth_token = App.get('escience_token');
					// Push to store the user retrieved from Django backend.
					self.store.push('user', {
						id : 1,
						user_id : user.get('user_id'),
						token : user.get('escience_token'),
						cluster : user.get('cluster')
					});
					// Set the text in login screen to blank and redirect to welcome screen
					self.set('loginFailed', false);
					self.set('controllers.application.loggedIn', true);
					self.set('token', '');
					var previousTransition = self.get('previousTransition');
					if (previousTransition){
						self.set('previousTransition', null);
						previousTransition.retry();
					}else{
						self.transitionToRoute('user.welcome');	
					}	
                    
				}, function(reason) {
					// Failed login.
					console.log(reason.errorThrown);
					self.set('loginFailed', true);
					self.set('controllers.application.loggedIn', false);
					self.set('token', '');
				});

			}
		},
		dismiss : function(){
			$('#token').focus();
			$('#id_alert_wrongtoken > button').click();
			this.set('loginFailed', false);
		},
		visit_okeanos : function(){
		    $('#token').focus();
		    window.open(this.get('okeanos_api_url'),'_blank');
		},
	},
	
	runTimer : function() { 
		var self = this; 
		this.set("runLater", Ember.run.later(self, function() {
			self.set('controllers.application.loggedIn', false);
			self.set('token', '');
			self.transitionToRoute('user.logout');
        }, self.get('logout_time_limit')));
	},
	
	cancelRunTimer : function(){
		Ember.run.cancel(this.get("runLater"));
	}
}); 
