// Help Images controller
App.HelpImagesController = Ember.Controller.extend({
	orkaImages : [],
	active_image_uuid : '',
	active_image_loader : function(){
	    this.send('setActiveImage',this.get('active_image_uuid'));
	    return '';
	}.property('orkaImages','active_image_uuid'),
	actions : {
	    setActiveImage : function(image_pithos_uuid){
	        for (i=0;i<this.get('orkaImages').length;i++){
	            if (this.get('orkaImages').objectAt(i).get('image_pithos_uuid') == image_pithos_uuid){
	                this.set('active_image',image_pithos_uuid);
	                this.get('orkaImages').objectAt(i).set('active_image',true);
	            }else{
	                this.get('orkaImages').objectAt(i).set('active_image',false);
	            }
	        }
	    }
	}
});
