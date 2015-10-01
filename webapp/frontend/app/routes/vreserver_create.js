// VRE server Create route
App.VreserverCreateRoute = App.RestrictedRoute.extend({
    // model for create VRE server choices (input form)
    model : function() {
        $.loader.close(true);
        return this.store.find('vreserver');
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
            this.controller.send('find_last_config');
        },
        willTransition: function(){
            // leaving this route
            this.controller.send('reset');
        }
    }
});