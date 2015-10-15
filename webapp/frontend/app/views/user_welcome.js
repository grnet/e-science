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
		this.addObserver('controller.filtered_clusters.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
            });
        });
        this.addObserver('controller.filtered_vreservers.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
            });
        });
        this.addObserver('controller.filtered_dsls.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
            });
        });
		$(function() {
			$("[data-toggle='tooltip']").tooltip();
			var tab_element = $("#id_userclusters_tab");
			window.scrollTo(tab_element.offsetLeft, tab_element.offsetTop);
		});
	},
	willDestroyElement : function() {
		this.removeObserver('controller.sorting_info');
		this.removeObserver('controller.count');
		this.removeObserver('controller.filtered_clusters.[]');
		this.removeObserver('controller.filtered_vreservers.[]');
		this.removeObserver('controller.filtered_dsls.[]');
	}
});
