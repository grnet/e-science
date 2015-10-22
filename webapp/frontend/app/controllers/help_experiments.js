// Help Experiments controller
App.HelpExperimentsController = Ember.Controller.extend({
	needs : 'application',
	user_theme_changed : function(){
        var new_theme = this.get('controllers.application').get('user_theme');
        this.set('user_theme',new_theme);
    }.observes('controllers.application.user_theme'),
});
