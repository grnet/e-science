// View for memory selection buttons
App.MEMSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton', ':btn', ':btn-primary', ':btn-xs'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // on click    
    click: function () {
	// for this controller, trigger the mem_selection and send the value
        this.get('controller').send('mem_selection', this.get('value'));
    }
});
