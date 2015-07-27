// User Welcome view
App.UserWelcomeView = Ember.View.extend({
	didInsertElement : function() {
		// performance heavy, prefer the addObserver implementation below
		// $(this.get('element')).on('mousemove',function(){
		// $("[data-toggle='tooltip']").tooltip();
		// });
		var self = this;
		this.addObserver('controller.sorting_info', function() {
			Ember.run.scheduleOnce('afterRender', self, function() {
				$("[data-toggle='tooltip']").tooltip();
			});
		});
		this.addObserver('controller.count', function(){
			Ember.run.scheduleOnce('afterRender', self, function() {
				$("[data-toggle='tooltip']").tooltip();
			});
		});
		$(function() {
			$("[data-toggle='tooltip']").tooltip();
		});
	},
	willDestroyElement : function() {
		this.removeObserver('controller.sorting_info');
		this.removeObserver('controller.count');
	}
});
