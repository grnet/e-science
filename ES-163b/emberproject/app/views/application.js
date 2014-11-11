// Login view
// After user submits ~okeanos token, sends it to login controller
Orka.UserLoginView = Ember.View.extend({
	submit : function() {
		var text = this.get('controller.token');
		this.get('controller').send('login', text);
	}
});

Orka.CPUSelButView = Em.View.extend({
    tagName: 'button',
    classNameBindings: ['isRed:emberbutton'],
    isRed: true,
    attributeBindings: ['disabled'],
    click: function () {
        this.get('controller').send('cpu_selection', this.get('name'));
    }
});