// Login view
// After user submits ~okeanos token, sends it to login controller
App.UserLoginView = Ember.View.extend({
	// on submit
	submit : function() {
		// retrieve token
		var text = this.get('controller.token');
		// send it to the login action of the login controller
		this.get('controller').send('login', text);
	},
	didInsertElement : function() {
		$('#token').focus();
	}
});
