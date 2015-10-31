// Features/videos controller
App.FeaturesVideosController = Ember.Controller.extend({
	STATIC_URL : DJANGO_STATIC_URL,
	orka_ui_videos : function(){
	    var arrVideos = [];
	    var vids_by_row = 2;
	    arrVideos.pushObject(Ember.create.object({
	        src : 'https://www.youtube.com/embed/y2Ky3Wo37AY',
	        aspect : '16by9', // options: 16by9 , 4by3
	        footer : 'Video 1, Row 1, 16x9 Aspect',
	    }));
	    arrVideos.pushObject(Ember.create.object({
            src : 'https://www.youtube.com/embed/y2Ky3Wo37AY',
            aspect : '16by9', // options: 16by9 , 4by3
            footer : 'Video 1, Row 1, 16x9 Aspect',
        }));
        arrVideos.pushObject(Ember.create.object({
            src : 'https://www.youtube.com/embed/y2Ky3Wo37AY',
            aspect : '4by3', // options: 16by9 , 4by3
            footer : 'Video 1, Row 1, 16x9 Aspect',
        }));
	}.property()
});