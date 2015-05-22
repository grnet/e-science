attr = App.attr;
// Information about user (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), 			// okeanos token
	user_id : attr('number'), 			// user_id in backend database
	// may have more than one clusters
	user_name : attr('string'),          // user name or email
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
	ram_master : attr(),
	disk_master : attr(),
	cpu_slaves : attr(),
	ram_slaves : attr(),
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
	hdfs_overview : function() {
		// overview for hdfs URL=master_IP:50070
		return 'http://' + this.get('master_IP') + ':50070';
	}.property('master_IP'),
	browse_hdfs : function() {
		// hdfs browse URL=master_IP:50070/explorer.html#/
		return 'http://' + this.get('master_IP') + ':50070/explorer.html#/';
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
		case "2":
			return "glyphicon glyphicon-hourglass text-warning";
		default:
			return "glyphicon glyphicon-question-sign text-muted";
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_status_verbose : function(){
		var cluster_status = this.get('cluster_status');
		var hadoop_status = this.get('hadoop_status');
		var state = this.get('state');
		if (cluster_status == '1' && hadoop_status == '2'){
			return state;
		}else
		{
			return '';
		}
	}.property('hadoop_status', 'cluster_status'),
	hadoop_action_start_disabled : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		switch (status){
		case "0":
			return false;
		default:
			return true;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_action_stop_disabled : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		switch (status){
		case "1":
			return false;
		default:
			return true;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_action_format_disabled : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		switch (status){
		case "0":
			return false;
		case "1":
			return false;
		default:
			return true;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_status_active : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			status = "0";
		}
		switch (status){
		case "1":
			return true;
		default:
			return false;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_status_class_start : function(){
		return "glyphicon glyphicon-play text-success";
	}.property(),
	hadoop_status_class_stop : function(){
		return "glyphicon glyphicon-stop text-danger";
	}.property(),
	hadoop_status_class_format : function(){
		return "glyphicon glyphicon-erase text-warning";
	}.property(),
	cluster_name_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var cluster_name_id = "id_".concat("cluster_name_",cluster_name_sort);
		return cluster_name_id;	
	}.property('cluster_name'),
	cluster_status_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var cluster_status_id = "id_".concat("cluster_status_",cluster_name_sort);
		return cluster_status_id;	
	}.property('cluster_name'),
	hadoop_status_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var hadoop_status_id = "id_".concat("hadoop_status_",cluster_name_sort);
		return hadoop_status_id;	
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
	hadoop_start_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var start_id = "id_".concat("hadoop_start_",cluster_name_sort);
		return start_id;	
	}.property('cluster_name'),
	hadoop_stop_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var stop_id = "id_".concat("hadoop_stop_",cluster_name_sort);
		return stop_id;	
	}.property('cluster_name'),
	hadoop_format_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var format_id = "id_".concat("hadoop_format_",cluster_name_sort);
		return format_id;	
	}.property('cluster_name'),
	cluster_confirm_id : function (){
		var cluster_name_sort = this.get('cluster_name').slice(7);
		var confirm_id = "id_".concat("confirm_",cluster_name_sort);
		return confirm_id;	
	}.property('cluster_name'),
	cluster_confirm_action : function(key, value){
		this.set('confirm_action', value);
		return this.get('confirm_action');
	}.property(),
	cluster_confirm_action_verbose : function(key, value){
		var confirm_action = this.get('cluster_confirm_action');
		switch(confirm_action){
		case 'cluster_delete':
			return 'Destroy Cluster';
		case 'hadoop_start':
			return 'Start Hadoop';
		case 'hadoop_stop':
			return 'Stop Hadoop';
		case 'hadoop_format':
			return 'Format HDFS';
		default:
			return 'Confirm';
		}
	}.property('cluster_confirm_action'),
	cluster_hadoop_status : function()
	{
  		var status = this.get('hadoop_status');
  		var cluster_status = this.get('cluster_status');
  		if (cluster_status !== "1"){
   			status = "0";
  		}
  		switch (status){
  			case "0":
   				return "STOPPED";
  			case "1":
   				return "STARTED";
  			case "2":
   				return "PENDING";
  			default:
   				return "";
  		}
 	}.property('hadoop_status','cluster_status')
});

App.Usermessages = DS.Model.extend({
	// msg_types: 'default', 'primary', 'info', 'success', 'warning', 'danger'
	msg_type : attr('string'),
	msg_text : attr('string'),
	inc: function(){
		return Number(this.get('id'))+1;
	}.property(),
	msg_type_to_list_style : function(){
		var base_type = this.get('msg_type');
		return 'list-group-item-'+base_type+' spacious';
	}.property('msg_type'),
	msg_type_to_text_style : function(){
		var base_type = this.get('msg_type');
		return 'text-'+base_type;
	}.property('msg_type'),
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