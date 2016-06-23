// Login view
// After user submits ~okeanos token, sends it to login controller
App.UserLoginView = Ember.View.extend({
	// on submit
	submit : function() {
		// retrieve token
		var text = this.get('controller.token');
		// send it to the login action of the login controller
		this.get('controller').send('login', text);
		return false; // to avoid re-fresh to homepage
	},
	didInsertElement : function() {
		$('#token').focus();
	}
});
