// view for create cluster button
App.CreateClusterButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton'],
    // html attributes, custom (e.g. name) should be defined here
    attributeBindings: ['disabled'],
    // on click
    click: function () {
	// for this controller, trigger the go_to_create action
        this.get('controller').send('go_to_create');
    }
});