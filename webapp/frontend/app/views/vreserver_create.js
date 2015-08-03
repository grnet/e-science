// VreserverCreate View
App.VreserverCreateView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
			$('[data-toggle="popover"]').popover();
		});
	},
}); 