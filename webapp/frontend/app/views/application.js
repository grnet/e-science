// Application View (navbar)
App.ApplicationView = Ember.View.extend({
	didInsertElement : function() {
		$(function() {
            $('[data-toggle="popover"]').popover();
            $('[data-toggle="tooltip"]').tooltip();
        });
	},
});