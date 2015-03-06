// View for ram selection buttons
App.MEMSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
        if(this.get('name') == "master_ram_button")
	{
	    this.set('elementId', "master_ram_" + this.get('value'));
	    return this._super();
	}
        if(this.get('name') == "slaves_ram_button")
	{
	    this.set('elementId', "slaves_ram_" + this.get('value'));
	    return this._super();
	}
    },        
    // on click    
    click: function () {
	// for this controller, trigger the ram_selection and send the value
        this.get('controller').send('ram_selection', this.get('value'), this.get('name'));
    }
});
