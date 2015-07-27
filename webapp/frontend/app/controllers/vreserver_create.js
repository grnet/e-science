// VRE Server Create controller
App.VreserverCreateController = Ember.Controller.extend({
	needs : ['userWelcome', 'vreserverManagement'],
	vreImages : [],
	boolean_no_project : function(){
	    return Ember.isEmpty(this.get('selected_project_id'));
	}.property('selected_project_id'),
	selected_project_description : function(){
	    return !Ember.isEmpty(this.get('selected_project_id')) ? this.get('content').objectAt(this.get('selected_project_id')-1).get('project_name_clean') : '';
	}.property('selected_project_id'),
	selected_project_images : function(){
	    return !Ember.isEmpty(this.get('selected_project_id')) ? this.get('content').objectAt(this.get('selected_project_id')-1).get('vre_choices') : [];
	}.property('selected_project_id'),
	selected_project_sshkeys : function(){
	    return !Ember.isEmpty(this.get('selected_project_id')) ? this.get('content').objectAt(this.get('selected_project_id')-1).get('ssh_keys_names') : [];
	}.property('selected_project_id'),
	selected_image_description : function(){
	    return !Ember.isEmpty(this.get('selected_image_id')) ? this.get('selected_project_images')[this.get('selected_image_id')] : '';
	}.property('selected_image_id', 'selected_project_id'),
	vre_categories : function(){
        return !Ember.isEmpty(this.get('selected_project_id')) ? ['Portal/Cms','Wiki','Project Management'] : [];
    }.property('selected_project_images')
});
