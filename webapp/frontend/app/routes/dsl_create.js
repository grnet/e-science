// Escience reproducible research DSL create route
App.DslCreateRoute = App.RestrictedRoute.extend({
    // model for create DSL choices (input form)
    model : function() {
        $.loader.close(true);
        var promise = this.store.fetch('user',1);
        promise.then(function(user){
            var dsls = user.get('dsls');
            return dsls;
        },function(reason){
            console.log(reason.message);
        });
        return promise;
    },
    deactivate : function(){
        // left this route
        //this.controller.send('reset');
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
            //this.controller.send('reset');
        }
    }
});
