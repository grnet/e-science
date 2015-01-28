// User Welcome view
App.UserWelcomeView = Ember.View.extend({
	didInsertElement : function() {
		// todo: need a way to refresh when the partial is re-rendered that's performance friendly
		// $(this.get('element')).on('mousemove',function(){
		// $("[data-toggle='tooltip']").tooltip();
		// });
		this.addObserver('controller.sortdir', function() {
			var that = this;
			Ember.run.scheduleOnce('afterRender', that, function() {
				$("[data-toggle='tooltip']").tooltip();
			});
		});
		$(function() {
			$("[data-toggle='tooltip']").tooltip();
		});
	},
	willDestroyElement : function() {
		this.removeObserver('controller.sortdir');
	}
});
