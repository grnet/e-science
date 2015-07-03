App.ClusterManagementController = Ember.Controller.extend({
	
	needs : 'clusterCreate',
	hue_login_message: 'TEST',
	
	message_hue_login : function(){
		this.get('hue_login_message');
	}.property(), //.on('init')
	actions : {
		help_hue_login : function(help_msg){
			this.set('hue_login_message', help_msg);
		},
		
	}
});