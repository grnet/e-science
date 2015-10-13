// DslManagement View
App.DslManagementView = Ember.View.extend({
	didInsertElement : function(data) {
        // add delayed initialization or manual observers
        Ember.run.once(this, function(){
            PR.prettyPrint();
        },200);
	},
	willDestroyElement : function() {
        // remove manual observers here
    }
}); 