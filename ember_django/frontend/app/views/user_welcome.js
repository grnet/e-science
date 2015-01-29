// User Welcome view
App.UserWelcomeView = Ember.View.extend({
	didInsertElement : function() {
		// performance heavy, prefer the addObserver implementation below
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
