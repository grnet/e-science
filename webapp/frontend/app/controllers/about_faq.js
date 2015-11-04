// About/FAQ controller
App.AboutFaqController = Ember.Controller.extend({
    faq_by_category : function(){
        /*
         *  [{'category':'category_name','faqitems':[item1,item2,item3,..]},...]
         */
        var result = [];
        var content = this.get('content').sortBy('faq_category','faq_date');
        content.forEach(function(item) {
            var category = item.get('faq_category');
            var found = result.findBy('category', category);
            if (!found) {
                result.pushObject(Ember.Object.create({
                    category : category,
                    faqitems : []
                }));
            }
            Ember.set(item,'collapse_id','collapse%@'.fmt(item.get('id')));
            Ember.set(item,'collapse_href','#collapse%@'.fmt(item.get('id')));
            Ember.set(item,'faq_answer',Ember.String.htmlSafe(item.get('faq_answer')));
            result.findBy('category',category).get('faqitems').pushObject(item);
        });
        return result;
    }.property('content.[]','content.@each','content.isLoaded'),
    boolean_no_faqitems : function(){
        return Ember.isEmpty(this.get('faq_by_category')) || this.get('faq_by_category').length < 1;
    }.property('faq_by_category.[]')
});
