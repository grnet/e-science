// Login view
// After user submits ~okeanos token, sends it to login controller
Orka.UserLoginView = Ember.View.extend({
	submit : function() {
		var text = this.get('controller.token');
		this.get('controller').send('login', text);
	}
}); 