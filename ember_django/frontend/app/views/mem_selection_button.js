// View for memory selection buttons
App.MEMSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton', ':btn', ':btn-primary', ':btn-xs'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
        if(this.get('name') == "master_mem_button")
	{
	    this.set('elementId', "master_mem_" + this.get('value'));
	    return this._super();
	}
        if(this.get('name') == "slaves_mem_button")
	{
	    this.set('elementId', "slaves_mem_" + this.get('value'));
	    return this._super();
	}
    },        
    // on click    
    click: function () {
	// for this controller, trigger the mem_selection and send the value
        this.get('controller').send('mem_selection', this.get('value'), this.get('name'));
    }
});
