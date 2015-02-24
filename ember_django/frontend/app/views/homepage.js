// Homepage View
App.HomepageView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
			$("[data-toggle='tooltip']").tooltip();
		});
	},
});