App.ChoiceSelectController = Ember.Controller.extend({
	actions : {
		ThemeWhite: false,
		ThemeChoice : function() {
		if (this.get('ThemeWhite')){
			THEME_URL="/bootstrap.united.orca.css";
			return THEME_URL;
		}else {
			THEME_URL="/bootstrap.orca.css";
			return THEME_URL;
		}
	}.property('ThemeWhite'),
	THEME : THEME_URL,
	},	
});
