// Features/screenshots controller
App.FeaturesScreenshotsController = Ember.Controller.extend({
	STATIC_URL : DJANGO_STATIC_URL,
	orka_ui_screens : function(){
	    var arrScreens = [];
	    var prefix = this.get('STATIC_URL');
	    for (i=1;i<67;i++){
	        var pad2 = ('00'+i).slice(-2);
	        arrScreens.pushObject(Ember.Object.create({
	            active : i==1 ? true : false,
	            slide_to : i-1,
	            src : '%@images/orkaUIimage%@.png'.fmt(prefix,pad2),
	            alt : '~orka Web GUI #%@'.fmt(pad2)
	        }));
	    }
	    return arrScreens;
	}.property()
});