App.UserThemeView = Ember.View.extend({	 
	tagName: 'li',
    attributeBindings: ['name', 'value'],
    // initialization
    init: function() {
        // set id
        if(this.get('name') == "myLinkB")
	{
	    this.set('elementId', this.get('value'));
	    return this._super();
	}
        if(this.get('name') == "myLinkW")
	{
	    this.set('elementId', this.get('value'));
	    return this._super();
	}
    },    
    // on click
    click: function () {
    	console.log(this.get('value'));
        this.get('controller').send('user_theme_selection', this.get('value'));
    }
});
