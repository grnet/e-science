// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
Orka.UserWelcomeController = Ember.Controller.extend({
        logout : function() {
                this.transitionToRoute('user.logout');
        },
        createcluster : function() {
                this.transitionToRoute('createcluster.index');
        }
});