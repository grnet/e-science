// Help Personal Orka controller
App.HelpPersonalorkaController = Ember.Controller.extend({
	needs : 'application',
	user_theme_changed : function(){
        var new_theme = this.get('controllers.application').get('user_theme');
        this.set('user_theme',new_theme);
    }.observes('controllers.application.user_theme'),
    actions : {
        selectTab : function(tab){
            var element = '.nav-tabs a[href="%@"]'.fmt(tab);
            $(element).tab('show');
        }
    }
});
