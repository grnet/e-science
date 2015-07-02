App.ClusterManagementController = Ember.Controller.extend({
	
	needs : 'clusterCreate',
	hue_login_message: '',
	
	message_hue_login : function(){
		this.get('hue_login_message');
	}.on('init'),
	actions : {
		help_hue_login_post : function(help_msg){
			this.set('hue_login_message', help_msg);
		},
		help_hue_login : function(){
			this.get('message_hue_login');
		},
		
	}
});