attr = App.attr;
// Information about user (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), 			// okeanos token
	user_id : attr('number'), 			// user_id in backend database
	user_name : attr('string'),         // user name or email
	user_theme : attr('string'),        // user's theme in backend database
	cluster : attr(), // number of user active clusters
	vrenum : attr(), // number of user active VREs
	dslnum : attr(), // number of user DSLs
	escience_token : attr(),
    master_vm_password: attr('string'),
    error_message: attr('string'),
    clusters : DS.hasMany('usercluster', {
        async : true,
        inverse : 'user'
    }),                           // user cluster records
    vreservers : DS.hasMany('uservreserver', {
        async : true,
        inverse : 'user'
    }),                           // user VRE server records
    dsls : DS.hasMany('dsl', {
        async : true,
        inverse : 'user'
    })
});

// Information about user's DSLs
App.Dsl = DS.Model.extend({
    dsl_name : attr('string'),
    action_date : attr('isodate'),
    cluster_id : attr('number'),
    pithos_path : attr('string'),
    task_id : attr(), 
    state : attr(),
    // user that created the VRE
    user : DS.belongsTo('user', {
        inverse : 'dsls'
    }),
    // computed properties
    class_button_dsl_destroy : function(){
        return !Ember.isEmpty(this.get('pithos_path')) ? "glyphicon glyphicon-trash text-danger" : "";
    }.property('pithos_path'),
    action_dsl_confirm : function(key, value){
        this.set('confirm_action', value);
        return this.get('confirm_action');
    }.property(),
    description_action_dsl_confirm : function(key, value){
        var confirm_action = this.get('action_dsl_confirm');
        switch(confirm_action){
        case 'dsl_delete':
            return 'Delete DSL';
        default:
            return 'Confirm';
        }
    }.property('action_dsl_confirm'),
    id_dsl_name : function(key){
        return '%@%@'.fmt(key,this.get('dsl_name'));
    }.property('dsl_name'),
    id_pithos_path : function(key){
        return '%@%@'.fmt(key,this.get('dsl_name'));
    }.property('dsl_name'),
    id_dsl_confirm : function(key){
        return '%@%@'.fmt(key,this.get('dsl_name'));
    }.property('dsl_name'),
    id_dsl_destroy : function(key){
        return '%@%@'.fmt(key,this.get('dsl_name'));
    }.property('dsl_name'),
    id_dsl_create : function(key) {
        return '%@%@'.fmt(key,this.get('dsl_name'));       
    }.property('dsl_name')
});

// Information about user's VREs
App.Uservreserver = DS.Model.extend({
    server_name : attr('string'), 
    action_date : attr('isodate'), 
    server_status : attr('string'),
    server_IP : attr('string'),
    ssh_key_selection : attr('string'), // ssh_key_name
    cpu : attr(), 
    ram : attr(), 
    disk : attr(), 
    disk_template : attr(),
    os_image : attr(),
    project_name : attr(), 
    task_id : attr(), 
    state : attr(),
    admin_password : attr('string'),
    admin_email : attr('string'),
    // user that created the VRE
    user : DS.belongsTo('user', {
        inverse : 'vreservers'
    }),
    // computed properties
    vre_okeanos_faq: function(){
        // Return url with helpful info for setting up email port inside ~okeanos
        return 'https://okeanos.grnet.gr/support/faq/cyclades-why-is-port-x-closed-is-it-blocked-by-design/';
    }.property('os_image'),
    vre_readme_url: function(){
        // Return url with helpful info for docker operations in VRE servers
        return 'https://github.com/grnet/e-science/blob/master/orka/VRE_README.md';
    }.property('os_image'),
    class_vre_status : function (){
        var status = this.get('server_status');
        switch (status) {
        case "0":  //destroyed
            return "glyphicon glyphicon-trash text-danger";
        case "1":  //active
            return "glyphicon glyphicon-ok text-success";
        case "2":  //pending
            return "glyphicon glyphicon-time text-warning";
        case "3":  //failed
            return "glyphicon glyphicon-remove text-danger";
        default:   //unknown
            return "glyphicon glyphicon-question-sign text-muted";
        }
    }.property('server_status'),
    description_vre_status : function(){
        var status = this.get('server_status');
        switch (status) {
        case "0":
            return "DESTROYED";
        case "1":
            return "ACTIVE";
        case "2":
            return "PENDING";
        case "3":
            return "FAILED";
        default:
            return "UNKNOWN";
        }
    }.property('server_status'),
    resorted_status : function(){
        // pending > active > destroyed > failed 
        // 0 < 2(pending), 1 < 1(active), 2 < 0(destroyed), 3 < 3(failed)
        var priority = {"0":"2","1":"1","2":"0","3":"3"};
        return priority[this.get('server_status')];
    }.property('server_status'),
    boolean_vre_status_active : function(){
        return this.get('server_status') == "1" ? true : false;
    }.property('server_status'),
    boolean_vre_status_pending : function(){
        return this.get('server_status') == "2" ? true : false;
    }.property('server_status'),
    class_button_vre_destroy : function(){
        return this.get('boolean_vre_status_active') ? "glyphicon glyphicon-trash text-danger" : "";
    }.property('boolean_vre_status_active'),
    message_vre_status_pending : function(){
        var status = this.get('server_status');
        if (status == '2'){ // pending
            return this.get('state') || 'Pending...'; // message from celery if set
        }else{
            return '';
        }
    }.property('server_status'),
    action_server_confirm : function(key, value){
        this.set('confirm_action', value);
        return this.get('confirm_action');
    }.property(),
    description_action_server_confirm : function(key, value){
        var confirm_action = this.get('action_server_confirm');
        switch(confirm_action){
        case 'server_delete':
            return 'Destroy Server';
        default:
            return 'Confirm';
        }
    }.property('action_server_confirm'),
    // create dynamic html element ids
    server_name_noprefix : function(){
        // remove the '[orka]-' prefix
        return this.get('server_name').slice(7);
    }.property('server_name'),
    id_server_name : function(key){
        return '%@%@'.fmt(key,this.get('server_name_noprefix'));
    }.property('server_name_noprefix'),
    id_server_status :function(key){
        return '%@%@'.fmt(key,this.get('server_name_noprefix'));
    }.property('server_name_noprefix'),
    id_server_ip : function(key){
        return '%@%@'.fmt(key,this.get('server_name_noprefix'));
    }.property('server_name_noprefix'),
    id_server_confirm : function(key){
        return '%@%@'.fmt(key,this.get('server_name_noprefix'));
    }.property('server_name_noprefix'),
    id_server_destroy : function(key){
        return '%@%@'.fmt(key,this.get('server_name_noprefix'));
    }.property('server_name_noprefix'),
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
	replication_factor : attr(),
	dfs_blocksize : attr(),
	// user that created the cluster
	user : DS.belongsTo('user', {
		inverse : 'clusters'
	}),
	// computed properties
	cluster_name_noprefix : function(){
        // remove the '[orka]-' prefix
        return this.get('cluster_name').slice(7);
    }.property('cluster_name'),
    cluster_slaves_num : function(){
        return this.get('cluster_size')-1;
    }.property('cluster_size'),
	workflow_link : function(){
		return 'http://%@:8888/oozie/editor/workflow/new/'.fmt(this.get('master_IP'));
	}.property('master_IP'),
	workflow_enabled : function(){
		if (this.get('ecosystem_or_cloudera') && (this.get('hadoop_status_active'))){
			return 'a';
		}else{
			return 'b';
		}
	}.property('ecosystem_or_cloudera', 'hadoop_status_active'),
	workflow_tooltip_msg : function(){
		if (this.get('selected_image') == 0){
			return 'First login in Hue with username hduser';
		} else if (this.get('selected_image') == 1){
			return 'First login in Hue with username hdfs';
		}
	}.property('selected_image'),
	cluster_url : function() {
		return 'http://%@:8088/cluster'.fmt(this.get('master_IP'));
	}.property('master_IP'),
	hdfs_overview : function() {
		// overview for hdfs URL=master_IP:50070
		return 'http://%@:50070'.fmt(this.get('master_IP'));
	}.property('master_IP'),
	selected_image : function() {
		// Images with functional HDFS browser
		var images_with_hdfs_browser = [/Ecosystem/, /CDH/, /Hue/];
		for (var i = 0; i < images_with_hdfs_browser.length; i++) {
	        if (images_with_hdfs_browser[i].test(this.get('os_image'))) {
	            return i;
	        }
		}
		return -1;
	}.property('os_image'),
	browse_hdfs : function() {
		// hdfs browse URL=master_IP:50070/explorer.html#/ if not Hue image
        // If Hue image, then browse URL=master_IP:8888/
        var hdfs_explorer_default = ':50070/explorer.html#/' ;
        if (this.get('selected_image') > -1) {
            hdfs_explorer_default = ':8888/filebrowser' ;
        }
		return 'http://%@%@'.fmt(this.get('master_IP'), hdfs_explorer_default);
	}.property('master_IP'),
	boolean_scale_cluster_applicable : function(){
	    var image = this.get('os_image');
	    var re = /Cloudera/i;
	    return !re.test(image);
	}.property('os_image'),
	ecosystem_or_cloudera : function() {
		if (this.get('selected_image') > -1 && this.get('selected_image') < 2) {
            return true;
        }else{
        	return false;
        }
	}.property('os_image'),
	oozie : function() {
		var oozie_browser = ':11000';
		return 'http://%@%@'.fmt(this.get('master_IP'), oozie_browser);
	}.property('master_IP'),
	hbase : function() {
		var hbase_browser = ':16010';
        if (this.get('selected_image') == 1) {
            hbase_browser = ':9095' ;
        }
		return 'http://%@%@'.fmt(this.get('master_IP'), hbase_browser);
	}.property('master_IP'),
	spark : function() {
		var spark_browser = ':8080';
        if (this.get('selected_image') == 1) {
            spark_browser = ':18080' ;
        }
		return 'http://%@%@'.fmt(this.get('master_IP'), spark_browser);
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
		case "3":
			return "FAILED";
		default:
			return "UNKNOWN";
		}
	}.property('cluster_status'),
	cluster_status_class : function()
	{
		var status = this.get('cluster_status');
		switch (status) {
		case "0":
			return "glyphicon glyphicon-trash text-danger";
		case "1":
			return "glyphicon glyphicon-ok text-success";
		case "2":
			return "glyphicon glyphicon-time text-warning";
		case "3":
			return "glyphicon glyphicon-remove text-danger";

		default:
			return "glyphicon glyphicon-question-sign text-muted";
		}
	}.property('cluster_status'),
	resorted_status : function(){
        // pending > active > destroyed > failed 
        // 0 < 2(pending), 1 < 1(active), 2 < 0(destroyed), 3 < 3(failed)
        var priority = {"0":"2","1":"1","2":"0","3":"3"};
        return priority[this.get('cluster_status')];
    }.property('cluster_status'),
	cluster_status_pending : function(){
		var status = this.get('cluster_status');
		if (status == '2'){
			return this.get('state') || 'Pending...';
		}else{
			return '';
		}
	}.property('cluster_status'),
	cluster_manage_enabled : function(){
	   var disabled = ['DESTROYED','FAILED'];
	   var status_verbose = this.get('cluster_status_verbose');
	   return !disabled.contains(status_verbose);	   
	}.property('cluster_status_verbose'),
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
			return "glyphicon glyphicon-trash text-danger";
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
	cluster_action_destroy_disabled : function(){
	    var status_final = ['ACTIVE','STARTED','STOPPED'];
	    var cluster_status = this.get('cluster_status_verbose');
        var hadoop_status = this.get('cluster_hadoop_status');
        return !(status_final.contains(cluster_status) && status_final.contains(hadoop_status));
	}.property('cluster_status_verbose','cluster_hadoop_status'),
	hadoop_status_verbose : function(){
		var cluster_status = this.get('cluster_status');
		var hadoop_status = this.get('hadoop_status');
		var state = this.get('state');
		if (cluster_status == '1' && (hadoop_status == '2' || hadoop_status == '3')){
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
			return true;
		}
		switch (status){
		case "0":
			return false;
		case "3":
		    return false;
		default:
			return true;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_action_stop_disabled : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			return true;
		}
		switch (status){
		case "1":
		    return false;
	    case "3":
	        return false;
		default:
			return true;
		}
	}.property('hadoop_status','cluster_status'),
	hadoop_action_format_disabled : function(){
		var status = this.get('hadoop_status');
		var cluster_status = this.get('cluster_status');
		if (cluster_status !== "1"){
			return true;
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
	cluster_scale_id : function(){
        var cluster_name_short = this.get('cluster_name').slice(7);
        var cluster_scale_id = "id_".concat("cluster_scale_",cluster_name_short);
        return cluster_scale_id;
    }.property('cluster_name'),
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
   				return "UNKNOWN";
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
