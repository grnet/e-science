// ClusterManagement View
App.ClusterManagementView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
			$('[data-toggle="popover"]').popover();
		});
	},	
}); 