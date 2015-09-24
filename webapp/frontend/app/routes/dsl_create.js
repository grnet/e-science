// Escience reproducible experiments DSL create route
App.DslCreateRoute = App.RestrictedRoute.extend({
    // model for create DSL choices (input form)
    model : function(params, transition) {
        $.loader.close(true);
        var promise = this.store.fetch('user',1);
        promise.then(function(user){
            return user.get('clusters');
        },function(reason){
            console.log(reason.message);
        });
        return promise;
    },
    setupController : function(controller, model){
        this._super(controller,model);
        controller.set('user_clusters',model.get('clusters'));
        controller.set('user_dsls',model.get('dsls'));
    },
    deactivate : function(){
        // left this route
        this.controller.send('reset');
    },
    actions : {
        error : function(err) {
            // to catch errors
            // for example 401 responses
            console.log(err['message']);
            this.transitionTo('user.logout');
        },
        didTransition : function(transition) {
            // came to this route
        },
        willTransition: function(){
            // leaving this route
            this.controller.send('reset');
        }
    }
});
