App.UserThemeController = Ember.Controller.extend({
	actions: {
		user_theme_selection: function(value) {
			console.log("received value is -->" + value);
			this.set('linkcss', value);
			console.log(linkcss);
			//changeCSS(value, 0);
			//location.reload();
		}
	}
});
