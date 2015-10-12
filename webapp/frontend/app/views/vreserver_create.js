// VreserverCreate View
App.VreserverCreateView = Ember.View.extend({
	didInsertElement : function() {
	    this.addObserver('controller.show_admin_password_input', function(){
            Ember.run.scheduleOnce('afterRender', self, function() {
                $('[data-toggle="popover"]').popover();
                $('[data-toggle="tooltip"]').tooltip();
            });
        });
		$(function() {
            $('[data-toggle="popover"]').popover();
            $('[data-toggle="tooltip"]').tooltip();
		});
	},
	willDestroyElement : function() {
        this.removeObserver('controller.show_admin_password_input');
    }
}); 