// DslCreate View
App.DslCreateView = Ember.View.extend({
    didInsertElement : function() {
        $(function() {
            $('[data-toggle="popover"]').popover();
            $('[data-toggle="tooltip"]').tooltip();
        });
    },
    willDestroyElement : function() {
        // if we have custom observers remove them here
    }
});