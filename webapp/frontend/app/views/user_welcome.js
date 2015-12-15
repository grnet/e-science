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
				$("[data-toggle='popover']").popover();
			});
		});
		this.addObserver('controller.count', function(){
			Ember.run.scheduleOnce('afterRender', self, function() {
				$("[data-toggle='tooltip']").tooltip();
				$("[data-toggle='popover']").popover();
			});
		});
		this.addObserver('controller.cluster_active_filter', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
                $("[data-toggle='popover']").popover();
            });
        });
        this.addObserver('controller.cluster_confirm_action_changed', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
                $("[data-toggle='popover']").popover();
            });
        });        
		this.addObserver('controller.filtered_clusters.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
                $("[data-toggle='popover']").popover();
            });
        });
        this.addObserver('controller.filtered_vreservers.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
                $("[data-toggle='popover']").popover();
            });
        });
        this.addObserver('controller.filtered_dsls.[]', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $("[data-toggle='tooltip']").tooltip();
                $("[data-toggle='popover']").popover();
            });
        });
		$(function() {
			$("[data-toggle='tooltip']").tooltip();
			$("[data-toggle='popover']").popover();
			var tab_element = $("#id_userclusters_tab");
			window.scrollTo(tab_element.offsetLeft, tab_element.offsetTop);
		});
	},
	willDestroyElement : function() {
		this.removeObserver('controller.sorting_info');
		this.removeObserver('controller.count');
		this.removeObserver('controller.cluster_active_filter');
		this.removeObserver('controller.cluster_confirm_action_changed');
		this.removeObserver('controller.filtered_clusters.[]');
		this.removeObserver('controller.filtered_vreservers.[]');
		this.removeObserver('controller.filtered_dsls.[]');
	}
});
