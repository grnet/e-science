// About/FAQ View
App.AboutFaqView = Ember.View.extend({
    didInsertElement : function(data) {
        var self = this;
        // add delayed initialization or manual observers
        function toggleArrow(e) {
            $(e.target).prev('.panel-heading').find("i.indicator").toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
            $(e.target).prev('.panel-heading').find("i.indicator").toggleClass('text-default text-info');
        }
        $('#id_faq_accordion').on('hidden.bs.collapse', toggleArrow);
        $('#id_faq_accordion').on('shown.bs.collapse', toggleArrow);
        },
    willDestroyElement : function() {
        // remove manual observers here
    }
});