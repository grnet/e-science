// view for disk selection buttons
App.DiskSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton', ':btn', ':btn-primary', ':btn-xs'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // on click
    click: function () {
	// for this controller, trigger the disk_selection and send the value
        this.get('controller').send('disk_selection', this.get('value'));
    }
});