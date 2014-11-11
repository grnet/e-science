// Index route (e.g localhost:port/) redirects to homepage
Orka.IndexRoute = Ember.Route.extend({
        redirect : function() {
                this.transitionTo('homepage');
        }
});
