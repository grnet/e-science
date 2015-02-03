App.UserThemeController = Ember.Controller.extend({
	actions : {		
		DarkTheme: function(user_theme) {
			changeCSS(user_theme, 0);
			//location.reload();
		},
		WhiteTheme: function(user_theme) {
			console.log("hello1");
			changeCSS(user_theme, 0);
			console.log("hello2");
		}
	}
});
