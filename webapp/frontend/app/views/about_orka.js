// About/Orka View
App.AboutOrkaView = Ember.View.extend({
    didInsertElement : function(data) {
        var self = this;
        // add delayed initialization or manual observers
        $(function() {
            $('[data-toggle="popover"]').popover();
            $('[data-toggle="tooltip"]').tooltip();
        });
        },
    willDestroyElement : function() {
        // remove manual observers here
    }
});