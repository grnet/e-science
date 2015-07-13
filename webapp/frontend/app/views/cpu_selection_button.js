// View used for CPU selection buttons
App.CPUSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
        if(this.get('name') == "master_cpus_button")
	{
	    this.set('elementId', "master_cpus_" + this.get('value'));
	    return this._super();
	}
        if(this.get('name') == "slaves_cpus_button")
	{
	    this.set('elementId', "slaves_cpus_" + this.get('value'));
	    return this._super();
	}
    },    
    // on click
    click: function () {
	// for this controller, trigger the CPU_selection and send the value
        this.get('controller').send('cpu_selection', this.get('value'), this.get('name'));
    }
});
