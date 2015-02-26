// ClusterCreate View
App.ClusterCreateView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
			$('[data-toggle="popover"]').popover();
		});
	},
}); 