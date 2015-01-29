// View used for theme selection choices
App.themeSelButView = Ember.View.extend({
	tagName: 'li',
	attributeBindings: ['value'],
	init : function() {
        window.alert("view before click");
	    if (this.get('value') == 'WhiteTheme') {
	    	ThemeWhite=true;
	    }
	    if (this.get('value') == 'BlackTheme') {
	    	ThemeWhite=false;
	    }
	    // on click
	    click: function () {
	    	window.alert("view on click");
	        this.get('controller').send('ThemeChoice', this.get('ThemeWhite'));	 
	 },
});