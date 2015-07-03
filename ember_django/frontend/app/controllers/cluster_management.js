App.ClusterManagementController = Ember.Controller.extend({
	
	needs : 'clusterCreate',
	hue_login_message: '',
	
	message_hue_login : function(){
		this.get('hue_login_message');
	}.property(),
	actions : {
		help_hue_login : function(help_msg){
			if (help_msg !== ''){
				this.set('hue_login_message', help_msg);
			}
		},		
	}
});