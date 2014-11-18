// view for disk selection buttons
App.DiskSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton', ':btn', ':btn-primary', ':btn-xs'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
        if(this.get('name') == "master_disk_button")
	{
	    this.set('elementId', "master_disk_" + this.get('value'));
	    return this._super();
	}
        if(this.get('name') == "slaves_disk_button")
	{
	    this.set('elementId', "slaves_disk_" + this.get('value'));
	    return this._super();
	}
    },     
    // on click
    click: function () {
	// for this controller, trigger the disk_selection and send the value
        this.get('controller').send('disk_selection', this.get('value'), this.get('name'));
    }
});