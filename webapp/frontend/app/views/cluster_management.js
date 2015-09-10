// ClusterManagement View
App.ClusterManagementView = Ember.View.extend({
	didInsertElement : function(data) {
	    var self = this;
		$(function() {
            $('[data-toggle="popover"]').popover();
            $('[data-toggle="tooltip"]').tooltip();
            self.controller.get('slaves_increment_loader') ? $('#id_slave_add').loader() : $.loader.close(true);
        });
        this.addObserver('controller.slaves_increment_loader', function(data){
            Ember.run.scheduleOnce('afterRender', self, function() {
                self.controller.get('slaves_increment_loader') ? $('#id_slave_add').loader() : $.loader.close(true);
                $("[data-toggle='tooltip']").tooltip();
            });
        });
	},
	willDestroyElement : function() {
        this.removeObserver('controller.slaves_increment_loader');
    }
}); 