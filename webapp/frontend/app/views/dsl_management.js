// DslManagement View
App.DslManagementView = Ember.View.extend({
	didInsertElement : function(data) {
	    var self = this;
        // add delayed initialization or manual observers
        this.addObserver('controller.user_theme', function(data){
            Ember.run.scheduleOnce('afterRender', self, function() {
                PR.prettyPrint();
            });
        });
        Ember.run.once(this, function(){
            PR.prettyPrint();
        },200);
	},
	willDestroyElement : function() {
        // remove manual observers here
        this.removeObserver('controller.user_theme');
    }
}); 