// View used for vm flavor selection buttons
App.VMFlavorSelButView = Ember.View.extend({
    tagName: 'button',
    // class names, :emberbutton for CSS style
    classNameBindings: [':emberbutton'],
    // html attributes, custom (e.g. name, value) should be defined here
    attributeBindings: ['disabled', 'name', 'value'],
    // initialization
    init: function() {
        // set id
	    if(this.get('name') == "vm_flavor_button_Master")
	{
	    this.set('elementId', "master_vm_falvors_" + this.get('value'));
	    return this._super();
	}
	    if(this.get('name') == "vm_flavor_button_Slave")
	{
	    this.set('elementId', "slave_vm_falvors_" + this.get('value'));
	    return this._super();
	}
    },    
    // on click
    click: function () {
	// for this controller, trigger the vm_flavor_selection and send the value
        this.get('controller').send('vm_flavor_selection', this.get('value'), this.get('name'));
    }
});
