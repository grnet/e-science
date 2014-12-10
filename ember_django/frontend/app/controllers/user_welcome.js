// Welcome route controller
App.UserWelcomeController = Ember.Controller.extend({
	needs : 'clusterCreate',
	output_message : '', // output message of create cluster script
	create_cluster_start : false, // flag to see if the transition is from create cluster button
});
