App.UserThemeView = Ember.View.extend({	 
	     
	click: function () {
		if(id==myLinkB) {
			console.log("dark theme");
			user_theme = 'styles/bootstrap.orca.css';
			this.get('controller').send('DarkTheme', user_theme);
		}		
		if(id==myLinkW) {
			console.log("white theme");
			user_theme = 'styles/bootstrap.united.orca.css';
			this.get('controller').send('WhiteTheme', user_theme);				
		}
	}
});