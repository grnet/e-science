// About/FAQ route
App.AboutFaqRoute = Ember.Route.extend({
    model : function(params, transition){
        var that = this;
        return this.store.fetch('faqitem',{}).then(function(faqitems){
            return faqitems.get('content');
        },function(reason){
            console.log(reason.message);
        });
    }
});
