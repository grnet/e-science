// Features/screenshots controller
App.FeaturesScreenshotsController = Ember.Controller.extend({
	STATIC_URL : DJANGO_STATIC_URL,
	screens_by_category : function(){
	    /*
         *  [{'category':'category_name','screens':[item1,item2,item3,..]},...]
         */
        var result = [];
        var prefix = this.get('STATIC_URL');
        var content = this.get('content').sortBy('screen_category');
        var inner_index = null;
        content.forEach(function(item,index) {
            var category = item.get('screen_category');
            var found = result.findBy('category', category);
            inner_index = index == 0 ? 0 : inner_index+1;
            if (!found) {
                var category_id = 'id_orka_carousel_%@'.fmt(Ember.String.underscore(category));
                var category_href = '#%@'.fmt(category_id);
                inner_index = 0;
                result.pushObject(Ember.Object.create({
                    category : category,
                    category_id : category_id,
                    category_href : category_href,
                    screens : []
                }));
            }
            Ember.set(item,'active',inner_index==0 ? true : false);
            Ember.set(item,'slide_to','%@'.fmt(inner_index));
            Ember.set(item,'src','%@images/%@'.fmt(prefix,item.get('screen_src')));
            Ember.set(item,'alt','%@'.fmt(item.get('screen_src')));
            result.findBy('category',category).get('screens').pushObject(item);
        });
        return result;
	}.property('content.[]','content.@each','content.isLoaded'),
	actions : {
	    carouselPlay : function(carousel){
	        $(carousel).carousel("cycle");
	    },
	    carouselPause : function(carousel){
	        $(carousel).carousel("pause");
	    }
	}
});