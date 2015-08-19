// Help VRE Images controller
App.HelpVreimagesController = Ember.Controller.extend({
	vreImages : [],
	active_image_uuid : '',
	active_image_loader : function(){
	    this.send('setActiveImage',this.get('active_image_uuid'));
	    return '';
	}.property('vreImages','active_image_uuid'),
	actions : {
	    setActiveImage : function(image_pithos_uuid){
	        for (i=0;i<this.get('vreImages').length;i++){
	            if (this.get('vreImages').objectAt(i).get('image_pithos_uuid') == image_pithos_uuid){
	                this.set('active_image',image_pithos_uuid);
	                this.get('vreImages').objectAt(i).set('active_image',true);
	            }else{
	                this.get('vreImages').objectAt(i).set('active_image',false);
	            }
	        }
	    }
	}
});
