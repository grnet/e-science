// View used for Storage selection buttons
App.StorageSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
	    this.set('elementId', this.get('value'));
	    return this._super();
	}, 
    // on click
    click: function () {
	// for this controller, trigger the disk_template_selection and send the value
        this.get('controller').send('disk_template_selection', this.get('value'), this.get('name'));
    }
});