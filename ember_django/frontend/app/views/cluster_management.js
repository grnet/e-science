// ClusterManagement View
App.ClusterManagementsView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
			$('[data-toggle="popover"]').popover();
		});
	},	
}); 