App.ApplicationController = Ember.Controller.extend({
        loggedIn: false,
        homeURL : function() {
                if (this.get('loggedIn')){
                        return "#/user/welcome";
                }else {
                        return "#/";
                }
        }.property('loggedIn'),
        STATIC_URL : '/static/',
});

