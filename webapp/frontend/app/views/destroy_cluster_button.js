// view for destroy cluster button
App.DestroyClusterButtonView = Ember.View.extend({
	tagName : 'button',
	// class names, :emberbutton for CSS style
	classNameBindings : [':emberbutton'],
	// html attributes, custom (e.g. name) should be defined here
	attributeBindings : ['disabled', 'value'],
	isVisible : true,
	// on click
	click : function() {
		// for this controller, trigger the go_to_destroy action
		// this.set('isVisible',false);
		// alert(String(this.get('isVisible')));
		// this.get('controller').send('go_to_confirm', this.get('value'));
		this.get('controller').send('go_to_destroy', this.get('value'));
	}
});
