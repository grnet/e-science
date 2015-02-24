attr = App.attr;
// Information about user (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), 			// okeanos token
	user_id : attr('number'), 			// user_id in backend database
	// may have more than one clusters
	user_theme : attr('string'),        // user's theme in backend database
	clusters : DS.hasMany('usercluster', {
		async : true,
		inverse : 'user'
	}), 						// user cluster records
	cluster : attr(),
	escience_token : attr(),
    master_vm_password: attr('string')
});

// Information about user's clusters
App.Usercluster = DS.Model.extend({
	cluster_name : attr('string'),
	action_date : attr('isodate'), // custom date transform implemented in store.js
	cluster_size : attr('number'),
	cluster_status : attr('string'),
	master_IP : attr('string'),
	cpu_master : attr(),
	mem_master : attr(),
	disk_master : attr(),
	cpu_slaves : attr(),
	mem_slaves : attr(),
	disk_slaves : attr(),
	disk_template : attr(),
	os_image : attr(),
	project_name : attr(),
	task_id : attr(),
	state : attr(),
	hadoop_status : attr(),
	// user that created the cluster
	user : DS.belongsTo('user', {
		inverse : 'clusters'
	}),
	cluster_url : function() {
		return 'http://' + this.get('master_IP') + ':8088/cluster';
	}.property('master_IP'),
	cluster_status_verbose : function() {
		var status = this.get('cluster_status');
		switch (status) {
		case "0":
			return "DESTROYED";
		case "1":
			return "ACTIVE";
		case "2":
			return "PENDING";
		default:
			return "UNKNOWN";
		}
	}.property('cluster_status'),
	cluster_status_class : function()
	{
		var status = this.get('cluster_status');
		switch (status) {
		case "0":
			return "glyphicon glyphicon-remove text-danger";
		case "1":
			return "glyphicon glyphicon-ok text-success";
		case "2":
			return "glyphicon glyphicon-time text-warning";

		default:
			return "glyphicon glyphicon-question-sign text-muted";
		}
	}.property('cluster_status'),
	cluster_hadoop_status_class : function()
	{
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		switch (status){
		case "0":
			return "glyphicon glyphicon-stop text-danger";
		case "1":
			return "glyphicon glyphicon-play text-success";
		default:
			return "glyphicon glyphicon-hourglass text-muted";
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_status_active : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		if (status == '1'){
			return true;
		}else{
			return false;
		}
	}.property('hadoop_status','cluster_status'),
	cluster_status_pending : function(){
		var status = this.get('cluster_status');
		if (status == '2'){
			return this.get('state') || 'Pending...';
		}else{
			return '';
		}
	}.property('cluster_status'),
	cluster_status_active : function(){
		var status = this.get('cluster_status');
		if (status == '1'){
			return true;
		}else{
			return false;
		}
	}.property('cluster_status'),
	cluster_status_class_destroy : function(){
		var status = this.get('cluster_status_active');
		if (status){
			return "glyphicon glyphicon-remove text-danger";
		}else{
			return '';
		}
	}.property('cluster_status_active'),
	hadoop_status_class_start : function(){
		return "glyphicon glyphicon-play text-success";
	}.property(),
	hadoop_status_class_stop : function(){
		return "glyphicon glyphicon-stop text-danger";
	}.property(),
	hadoop_status_class_format : function(){
		return "glyphicon glyphicon-hdd text-warning";
	}.property(),
	cluster_status_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var status_id = "id_".concat("status_",cluster_name_sort);
		return status_id;	
	}.property('cluster_name'),
	cluster_ip_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var ip_id = "id_".concat("ip_",cluster_name_sort);
		return ip_id;	
	}.property('cluster_name'),
	cluster_destroy_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var destroy_id = "id_".concat("destroy_",cluster_name_sort);
		return destroy_id;	
	}.property('cluster_name'),
	cluster_confirm_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var confirm_id = "id_".concat("confirm_",cluster_name_sort);
		return confirm_id;	
	}.property('cluster_name'),
	cluster_confirm_action : function(key, value){
		this.set('confirm_action', value);
		return this.get('confirm_action');
	}.property()
});

// App.User.reopenClass({
// FIXTURES : [{
// id : 1,
// token : "PLACEHOLDER",
// cluster : 3,
// clusters : [1, 2, 3]
// }]
// });
//
// App.UserCluster.reopenClass({
// FIXTURES : [{
// id : 1,
// cluster_name : "acluster",
// cluster_size : 5,
// cluster_status : "PENDING",
// user : 1
// }, {
// id : 2,
// cluster_name : "fcluster",
// cluster_size : 3,
// cluster_status : "ACTIVE",
// user : 1
// }, {
// id : 3,
// cluster_name : "ecluster",
// cluster_size : 12,
// cluster_status : "DESTROYED",
// user : 1
// }]
// });