App.ClusterManagementController = Ember.Controller.extend({
	
	needs : 'clusterCreate',
	hue_login_message : '',
	hue_message : '',
	orkaImages : [],
	
	actions : {
		help_hue_login : function(os_image){
			if (/Ecosystem/.test(os_image) || /Hue/.test(os_image)){
				this.set('hue_login_message', '<b>Hue first login</b><br><span class="text text-info">username : hduser</span>');
				this.set('hue_message', 'HUE');
			}else if (/CDH/.test(os_image)){
				this.set('hue_login_message', '<b>Hue first login</b><br><span class="text text-info">username : hdfs</span>');
				this.set('hue_message', 'CDH');
			}else if (/Debian/.test(os_image) || /Hadoop/.test(os_image)){
				this.set('hue_login_message', '');
				this.set('hue_message', '');
			}
			this.get('controllers.clusterCreate').set('hue_message', this.get('hue_message'));
		},
	}
});