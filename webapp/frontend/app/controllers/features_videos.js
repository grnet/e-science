// Features/videos controller
App.FeaturesVideosController = Ember.Controller.extend({
	needs : 'application',
	STATIC_URL : DJANGO_STATIC_URL,
	videos_per_row : function(key,value){
	    var video_settings = this.get('AppSettings').filterBy('section','Features').filterBy('property_name','Videos');
        return Ember.isEmpty(video_settings) ? null : JSON.parse(video_settings[0].get('property_value'))[key];
	}.property(),
	videos_by_row : function(){
	    /*
         *  [{'row':row_index, 'colspec': 'col-sm-x', 'videos':[item1,item2,item3,..]},...]
         *  1,2,3,4,6,12 are valid options for vids_per_row (12/vids_per_row must be a whole number).
         */
        var result = [];
        var content = this.get('content').sortBy('video_aspect');
        var row_index = null;
        var vids_per_row = Ember.isEmpty(this.get('videos_per_row')) ? 2 : Number(this.get('videos_per_row'));
        var bootstrap_cols = ((12/vids_per_row) | 0);
        content.forEach(function(item,index) {
            row_index = ((index/vids_per_row) | 0);
            var colspec = 'col col-sm-%@ hidden-xs'.fmt(bootstrap_cols);
            var found = result.findBy('row', row_index);
            if (!found) {
                result.pushObject(Ember.Object.create({
                    row : row_index,
                    colspec : colspec,
                    videos : []
                }));
            }
            Ember.set(item,'aspect','embed-responsive embed-responsive-%@'.fmt(item.get('video_aspect')));
            result.findBy('row',row_index).get('videos').pushObject(item);
        });
        return result;
	}.property('content.[]','content.@each','content.isLoaded')
});