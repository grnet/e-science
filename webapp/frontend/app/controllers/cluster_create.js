// Cluster Create controller
App.ClusterCreateController = Ember.Controller.extend({

	needs : ['userWelcome', 'clusterManagement'],
	orkaImages : [],
	info_popover_visible : false,
	project_index : 0, 		// index (position in the array) of the project
	project_current : '', 		// current project
	project_name : '', 		// name of the project
	cluster_size : 0, 		// Initial cluster size
	cluster_size_var : 0, 		// Initial cluster size keeper variable
	master_cpu_selection : 0, 	// Initial master_cpu_selection, appears in master cpu summary
	slaves_cpu_selection : 0, 	// Initial slaves_cpu_selection, appears in slaves cpu summary
	master_ram_selection : 0, 	// Initial master_ram_selection, appears in master ram summary
	slaves_ram_selection : 0, 	// Initial slaves_ram_selection, appears in slaves ram summary
	master_disk_selection : 0,	// Initial master_disk_selection, appears in master disk summary
	slaves_disk_selection : 0, 	// Initial slaves_disk_selection, appears in slaves disk summary
	cluster_name : '', 		// Initial cluster name, null
	replication_factor : '', 		// Replication_factor for hdfs
	default_replication_factor: '2', // Deafault replication_factor for hdfs
	dfs_blocksize : '', 		// Hadoop dfs_blocksize
	default_dfs_blocksize: '128', // Deafault dfs_blocksize for hdfs  is 128MB
	operating_system : 'Debian Base', // Preselected OS
	disk_temp : '', 	// Initial storage selection, common for master and slaves friendly to  user name
	cluster_size_zero : false, 	// for checking the available VMs, cluster size
	message : '', 			// message when user presses the create cluster button
	alert_mes_master_cpu : '', 	// alert message for master cpu buttons (if none selected)
	alert_mes_master_ram : '', 	// alert message for master ram buttons (if none selected)
	alert_mes_master_disk : '', 	// alert message for master disk buttons (if none selected)
	alert_mes_slaves_cpu : '', 	// alert message for slaves cpu buttons (if none selected)
	alert_mes_slaves_ram : '', 	// alert message for slaves ram buttons (if none selected)
	alert_mes_slaves_disk : '', 	// alert message for slaves disk buttons (if none selected)
	alert_mes_disk_template:'',		// alert message for disk template buttons (if none selected)
	alert_mes_cluster_name : '', 	// alert message for cluster name (if none selected)
	alert_mes_cluster_size : '', 	// alert message for cluster size (if none selected)
	alert_mes_replication_factor: '', // alert message for replication factor (if not integer or greater than slaves number)
	alert_mes_dfs_blocksize: '',	// alert message for cdfs blocksize (if not integer)
	warning_mes_replication_factor: '', // alert message for replication factor (if not default)
	warning_mes_dfs_blocksize: '',	// alert message for cdfs blocksize (if not default)
	project_details : '', 		// project details: name and quota(Vms cpus ram disk)
	name_of_project : '', 		// variable to set name of project as part of project details string helps parsing system project name
	ssh_key_selection : '',		// variable for selected public ssh_key to use upon cluster creation
	vm_flavor_selection_master : '', // Initial vm_flavor_selection_master
	vm_flavor_selection_slaves : '', // Initial vm_flavor_selection_slaves
	// Global variables for handling restrictions on master settings
	vm_flav_master_Small_disabled : false,  
	vm_flav_master_Medium_disabled : false, 
	vm_flav_master_Large_disabled : false, 
	// Global variable for handling restrictions on slaves settings
	vm_flav_slave_Small_disabled : false, 
	vm_flav_slave_Medium_disabled : false, 
	vm_flav_slave_Large_disabled : false,
	hue_message : '', 		// variable for Hue first login popover message
	version_message : '',  // message for components versions
	last_cluster_conf_checked: false,	// flag for last cluster configuration (when it is selected)
	last_conf_message : '',			// last configuration in message to be displayed on screen
	// selected project, image, cluster size, storage, from last configuration 
	// (to be displayed for the user)
	selected_project : '',	
	selected_image : '',
	selected_storage : '',
	alert_mes_last_conf : '',	// alert message when resources are not enough to apply last configuration
	list_of_roles : ['master', 'slaves'], // Possible roles for vms
	workflow_filter: false, // workflow_filter initial status
	workflow_filter_empty : 'no images available',
	admin_password: '', //password for hue superuser first login
	hue_in_image: false, //boolean to check if selected image has hue
	   
	// reads available ssh_keys
	// displays ssh_keys names in the drop-down list
	ssh_keys_av : function(){
		this.set('ssh_key_selection','');
		var keys =[];
		keys = this.get('content').objectAt(0).get('ssh_keys_names');
		return keys.sort();
	}.property('project_details'),
	
	// reads available projects
	// displays projects and available resources in the drop-down list
	// (spaces inserted just for alignment of projects-resources)
	projects_av : function() {
		this.reset_variables();
		this.set('project_current', '');
		this.set('project_name', '');
		var model = this.get('content');
		var projects = [];
		for (var i = 0; i < model.get('length'); i++) {
		    this.set('name_of_project',model.objectAt(i).get('project_name_clean'));
			projects[i] = model.objectAt(i).get('project_name_decorated');
			if ((projects[i]) == this.get('project_details'))
            { 
                if(this.get('last_cluster_conf_checked') == false)
                {
                    this.set('alert_mes_last_conf', '');
                }
                this.set('project_current', model.objectAt(i));
                this.set('project_name', model.objectAt(i).get('project_name'));
                this.set('project_index', i);               
            }
		}
		return projects.sort();
	}.property('project_details'),
	
	// For alerting the user if they have no project selected
	no_project_selected : function(){		
		var no_project = Ember.isBlank(this.get('project_name'));
		if (no_project){
			this.reset_project();
		}
		return no_project;
	}.property('project_name'),
	
	
	//Boolean to check if image has hue
	hue_image : function(){
		this.set('hue_in_image', false);
		this.set('alert_missing_input_admin_password','');
		for (var i=0; i<this.get('orkaImages').length; i++){
			if (this.get('orkaImages').objectAt(i).get('image_name') == this.get('operating_system')){
				for (var j=0; j<this.get('orkaImages').objectAt(i).get('image_components').length; j++) {
					if (this.get('orkaImages').objectAt(i).get('image_components').objectAt(j).name == 'Hue') {
						this.set('hue_in_image', true);
						break;
					}
				}
				break;
			}
		}
		return this.get('hue_in_image');
	}.property('operating_system'),

	//Images available after filtering for oozie component if option is selected
	images_available : function() {
		this.set('admin_password', '');
		var db_orka_images = [];
		var pithos_orka_images = [];
		var images = [];
		if (this.get('no_project_selected')) {
			return [];
		}
		pithos_orka_images = this.get('content').objectAt(this.get('project_index')).get('hadoop_choices');
		for (var i=0; i< this.get('orkaImages').length; i++){
			db_orka_images.push(this.get('orkaImages').objectAt(i).get('image_name'));
		}
		if (this.get('workflow_filter') == true) {
			for (var i = 0; i < pithos_orka_images.length; i++) {
				for (var k=0; k< db_orka_images.length; k++){
					if (pithos_orka_images[i]==db_orka_images[k]){
						for (var j = 0; j < this.get('orkaImages').objectAt(k).get('image_components').length; j++) {
							if (this.get('orkaImages').objectAt(k).get('image_components').objectAt(j).name == 'Oozie') {
								images.push(this.get('orkaImages').objectAt(k).get('image_name'));
							}
						}
					}
				}
			}
		} else {
			images = pithos_orka_images;
		}
		if (images.length == 0){
			images.push(this.get('workflow_filter_empty'));
		} else {
			this.set('operating_system', images[0]);
		}
		return images;
	}.property('workflow_filter', 'project_name'),

	// The total cpus selected for the cluster
	total_cpu_selection : function() {
		return (this.get('master_cpu_selection') + this.get('slaves_cpu_selection') * (this.size_of_cluster() - 1));
	}.property('master_cpu_selection', 'slaves_cpu_selection', 'project_details', 'cluster_size_var'),

	// Computes the available cpu each time total_cpu_selection changes
	cpu_available : function() {
		if (this.get('no_project_selected')){
			return 0;
		}
		var cpu_avail = this.get('content').objectAt(this.get('project_index')).get('cpu_av') - this.get('total_cpu_selection');
		return cpu_avail;
	}.property('total_cpu_selection', 'no_project_selected'),

	// The total ram selected for the cluster
	total_ram_selection : function() {
		return (this.get('master_ram_selection') + this.get('slaves_ram_selection') * (this.size_of_cluster() - 1));
	}.property('master_ram_selection', 'slaves_ram_selection', 'project_details', 'cluster_size_var'),

	// Computes the available ram each time total_ram_selection changes
	ram_available : function() {
		if (this.get('no_project_selected')){
			return 0;
		}
		ram_avail = this.get('content').objectAt(this.get('project_index')).get('ram_av') - this.get('total_ram_selection');
		return ram_avail;
	}.property('total_ram_selection', 'no_project_selected'),

	// The total disk selected for the cluster
	total_disk_selection : function() {
		return (this.get('master_disk_selection') + this.get('slaves_disk_selection') * (this.size_of_cluster() - 1));
	}.property('master_disk_selection', 'slaves_disk_selection', 'project_details', 'cluster_size_var'),

	// Computes the available disk each time total_disk_selection changes
	disk_available : function() {
		if (this.get('no_project_selected')){
			return 0;
		}
		disk_avail = this.get('content').objectAt(this.get('project_index')).get('disk_av') - this.get('total_disk_selection');
		return disk_avail;
	}.property('total_disk_selection', 'no_project_selected'),
	
	// alert if no available networks
	alert_mes_network : function(){
		net_av = this.get('content').objectAt(this.get('project_index')).get('net_av');
		var project_name = this.get('project_name');
		if (Number(net_av) <= 0 && !Ember.isBlank(project_name)){
			// this.get('disable_controls')(true);
			return 'No Networks available for this project.';
		}
	}.property('project_details'),
	
	// alert if no available floating ips
	alert_mes_float_ip : function(){
		float_ip_av = this.get('content').objectAt(this.get('project_index')).get('floatip_av');
		var project_name = this.get('project_name');
		if (Number(float_ip_av) <= 0 && !Ember.isBlank(project_name)){
			// this.get('disable_controls')(true);
			return 'No Floating IPs available for this project.';
		}
	}.property('project_details'),
	
	disable_controls : function(flag){
		var flag = flag && true || false;
		var aryButtons = $('.emberbutton');
		aryButtons.each(function(i, button){
			button.disabled = flag;
		});
		var aryControlIDs = ['os_systems','size_of_cluster','cluster_name','ssh_key','replication_factor','dfs_blocksize', 'id_components_info', 'id_hdfs_configuration', 'oozie_filter'];
		$.each(aryControlIDs,function(i, elementID){
			var element = $('#'+elementID);
			element.prop('disabled',flag);
		});
	},
	
	// Computes the maximum VMs that can be build with current flavor choices and return this to the drop down menu on index
	// If a flavor selection of a role(master/slaves) is 0, we assume that the role should be able to have at least the minimum option of the corresponding flavor
	// Available VMs are limited by user quota. First, they are filtered with cpu limits, then with ram and finally with disk. The result is returned to the drop down menu on index
	max_cluster_size_av : function() {
		this.set('alert_mes_cluster_size', '');
		var length = this.get('content').objectAt(this.get('project_index')).get('vms_av').length;
		var max_cluster_size_limited_by_current_cpus = [];
		var max_cluster_size_limited_by_current_ram = [];
		var max_cluster_size_limited_by_current_disks = [];
		var insufficient_net_or_ip = this.buttons();
		if (Ember.isEmpty(this.get('project_name')) || insufficient_net_or_ip){
			return [];
		}
		if (length < 2) {
			if (this.get('project_name') == undefined) {
				this.set('alert_mes_cluster_size', '');
			} else {
				this.set('alert_mes_cluster_size', 'Your VM quota are not enough to build the minimum cluster');
			}

			this.set('cluster_size_zero',true);
			return this.get('content').objectAt(this.get('project_index')).get('vms_av');
		}
		for (var i = 1; i < length; i++) {
			if (this.get('master_cpu_selection') == 0) {
				var master_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
			} else {
				var master_cpu = this.get('master_cpu_selection');
			}
			if (this.get('slaves_cpu_selection') == 0) {
				var slaves_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
			} else {
				var slaves_cpu = this.get('slaves_cpu_selection');
			}
			if ((this.get('content').objectAt(this.get('project_index')).get('cpu_av') - (master_cpu + ((this.get('content').objectAt(this.get('project_index')).get('vms_av')[i] - 1) * slaves_cpu))) < 0) {
				break;
			} else {
				for (var j = 0; j < i; j++) {
					max_cluster_size_limited_by_current_cpus[j] = this.get('content').objectAt(this.get('project_index')).get('vms_av')[j + 1];
				}
			}
		}
		length = max_cluster_size_limited_by_current_cpus.length;
		if (length == 0) {
			if (this.get('project_name') != '') {
				this.set('alert_mes_cluster_size', 'Your cpus quota are not enough to build the minimum cluster');
			}
			this.set('cluster_size_zero',true);
			return max_cluster_size_limited_by_current_cpus;
		}
		for ( i = 0; i < length; i++) {
			if (this.get('master_ram_selection') == 0) {
				var master_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var master_ram = this.get('master_ram_selection');
			}
			if (this.get('slaves_ram_selection') == 0) {
				var slaves_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var slaves_ram = this.get('slaves_ram_selection');
			}
			if ((this.get('content').objectAt(this.get('project_index')).get('ram_av') - (master_ram + ((max_cluster_size_limited_by_current_cpus[i] - 1) * slaves_ram))) < 0) {
				break;
			} else {
				for ( j = 0; j <= i; j++) {
					max_cluster_size_limited_by_current_ram[j] = max_cluster_size_limited_by_current_cpus[j];
				}
			}
		}
		length = max_cluster_size_limited_by_current_ram.length;
		if (length == 0) {
			if (this.get('project_name') != '') {
				this.set('alert_mes_cluster_size', 'Your ram quota are not enough to build the minimum cluster');
			}
			this.set('cluster_size_zero', true);
			return max_cluster_size_limited_by_current_ram;
		}
		for ( i = 0; i < length; i++) {
			if (this.get('slaves_disk_selection') == 0) {
				var slaves_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var slaves_disk = this.get('slaves_disk_selection');
			}
			if (this.get('master_disk_selection') == 0) {
				var master_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var master_disk = this.get('master_disk_selection');
			}
			if ((this.get('content').objectAt(this.get('project_index')).get('disk_av') - (master_disk + ((max_cluster_size_limited_by_current_ram[i] - 1) * slaves_disk))) < 0) {
				break;
			}
			for ( j = 0; j <= i; j++) {
				max_cluster_size_limited_by_current_disks[j] = max_cluster_size_limited_by_current_ram[j];
			}
		}
		if (max_cluster_size_limited_by_current_disks.length == 0) {
			this.set('alert_mes_cluster_size', 'Your disk size quota are not enough to build the minimum cluster');
			this.set('cluster_size_zero',true);
		}
		return max_cluster_size_limited_by_current_disks;
	}.property('total_cpu_selection', 'total_ram_selection', 'total_disk_selection', 'disk_temp', 'cluster_size_var', 'cluster_size', 'project_details'),

    
    flavor_settings : function(){
        var orkaFlavors = this.get('AppSettings').filterBy('section','VM_Flavor').sortBy('id');
        var objFlavors = {};
        for (i=0;i<orkaFlavors.length;i++){
            objFlavors[orkaFlavors[i].get('property_name')]=JSON.parse(orkaFlavors[i].get('property_value'));
        }
        return objFlavors;
    }.property(),
    list_of_flavors : ['cpu', 'ram', 'disk'], // List of flavors from kamaki except storage space
    list_of_flavor_sizes : function(){
        var orkaFlavors = this.get('AppSettings').filterBy('section','VM_Flavor').sortBy('id');
        var arrFlavors = [];
        var objFlavors = this.get('flavor_settings');
        for (i=0;i<orkaFlavors.length;i++){
            arrFlavors.push(orkaFlavors[i].get('property_name'));
        }
        return arrFlavors;
    }.property(),
    // Function to set master and slaves vm_flavor_selection
    vm_flavor_buttons_response: function (){
        var number_of_flavor_sizes = this.get('list_of_flavor_sizes').length;
        var number_of_roles = this.get('list_of_roles').length;
        for ( i = 0; i < this.number_of_flavor_sizes; i++){
            for ( j = 0; j < this.number_of_roles; j++){                
                if ((this.get('flavor_settings')[this.get('list_of_flavor_sizes')[i]]['cpu']==this.get(this.get('list_of_roles')[j] + '_cpu_selection')) && 
                    (this.get('flavor_settings')[this.get('list_of_flavor_sizes')[i]]['ram']==this.get(this.get('list_of_roles')[j] + '_ram_selection')) && 
                    (this.get('flavor_settings')[this.get('list_of_flavor_sizes')[i]]['disk']==this.get(this.get('list_of_roles')[j] + '_disk_selection'))){
                        this.set('vm_flavor_selection_' + this.get('list_of_roles')[j], this.get('list_of_flavor_sizes')[i]);
                }
                
            }
        }
    },
    // Functionality about coloring of the vm_flavor buttons and enable-disable responding to user events
	// First, remove colors from all vm_flavor buttons and then color the role's(master/slaves) selection
    vm_flavor_buttons : function() {
    	var elements = document.getElementsByName("vm_flavor_button_master");
		var length = elements.length;
		var vm_flavors = this.get('content').objectAt(this.get('project_index')).get('vm_flavors_choices');
		
		this.vm_flavor_buttons_response();
		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('vm_flav_master_Small_disabled')) {
				elements[0].disabled = true;
			} else {
				elements[0].disabled = false;
			}
			if (this.get('vm_flav_master_Medium_disabled')) {
				elements[1].disabled = true;
			} else {
				elements[1].disabled = false;
			}
			if (this.get('vm_flav_master_Large_disabled')) {
				elements[2].disabled = true;
			} else {
				elements[2].disabled = false;
			}
			if (!Ember.isEmpty(this.get('vm_flavor_selection_master'))) {
				var choice = document.getElementById("master_vm_flavors_".concat(this.get('vm_flavor_selection_master')));
				if ((this.get('master_cpu_selection') == this.get('flavor_settings')['Small']['cpu'])
					&&(this.get('master_ram_selection') == this.get('flavor_settings')['Small']['ram'])
					&&(this.get('master_disk_selection') == this.get('flavor_settings')['Small']['disk'])) {
					vm_flavor_newMaster_Id = "master_vm_flavors_Small";
					choice = document.getElementById(vm_flavor_newMaster_Id);
					choice.style.color = "white";
				} 
				if ((this.get('master_cpu_selection') == this.get('flavor_settings')['Medium']['cpu'])
					&&(this.get('master_ram_selection') == this.get('flavor_settings')['Medium']['ram'])
					&&(this.get('master_disk_selection') == this.get('flavor_settings')['Medium']['disk'])) {
					vm_flavor_newMaster_Id = "master_vm_flavors_Medium";
					choice = document.getElementById(vm_flavor_newMaster_Id);
					choice.style.color = "white";					
				}
				if ((this.get('master_cpu_selection') == this.get('flavor_settings')['Large']['cpu'])
					&&(this.get('master_ram_selection') == this.get('flavor_settings')['Large']['ram'])
					&&(this.get('master_disk_selection') == this.get('flavor_settings')['Large']['disk'])) {
					vm_flavor_newMaster_Id = "master_vm_flavors_Large";
					choice = document.getElementById(vm_flavor_newMaster_Id);
					choice.style.color = "white";
				}								
			}
		}
		var elements = document.getElementsByName("vm_flavor_button_slaves");
		var length = elements.length;
		var vm_flavors = this.get('content').objectAt(this.get('project_index')).get('vm_flavors_choices');
		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('vm_flav_slave_Small_disabled')) {
				elements[0].disabled = true;
			} else {
				elements[0].disabled = false;
			}
			if (this.get('vm_flav_slave_Medium_disabled')) {
				elements[1].disabled = true;
			} else {
				elements[1].disabled = false;
			}
			if (this.get('vm_flav_slave_Large_disabled')) {
				elements[2].disabled = true;
			} else {
				elements[2].disabled = false;
			}
			if (!Ember.isEmpty(this.get('vm_flavor_selection_slaves'))) {
				var choice = document.getElementById("slave_vm_flavors_".concat(this.get('vm_flavor_selection_slaves')));
				if ((this.get('slaves_cpu_selection') == this.get('flavor_settings')['Small']['cpu'])
					&&(this.get('slaves_ram_selection') == this.get('flavor_settings')['Small']['ram'])
					&&(this.get('slaves_disk_selection') == this.get('flavor_settings')['Small']['disk'])) {
					vm_flavor_newSlave_Id = "slave_vm_flavors_Small";
					choice = document.getElementById(vm_flavor_newSlave_Id);
					choice.style.color = "white";
				} 
				if ((this.get('slaves_cpu_selection') == this.get('flavor_settings')['Medium']['cpu'])
					&&(this.get('slaves_ram_selection') == this.get('flavor_settings')['Medium']['ram'])
					&&(this.get('slaves_disk_selection') == this.get('flavor_settings')['Medium']['disk'])) {
					vm_flavor_newSlave_Id = "slave_vm_flavors_Medium";
					choice = document.getElementById(vm_flavor_newSlave_Id);
					choice.style.color = "white";					
				}
				if ((this.get('slaves_cpu_selection') == this.get('flavor_settings')['Large']['cpu'])
					&&(this.get('slaves_ram_selection') == this.get('flavor_settings')['Large']['ram'])
					&&(this.get('slaves_disk_selection') == this.get('flavor_settings')['Large']['disk'])) {
					vm_flavor_newSlave_Id = "slave_vm_flavors_Large";
					choice = document.getElementById(vm_flavor_newSlave_Id);
					choice.style.color = "white";
				}							
			}
		}
	},

	// Functionality about coloring of the cpu buttons and enable-disable responding to user events
	// First, remove colors from all cpu buttons and then color the role's(master/slaves) selection
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available cpu, then disable the selected role button.
	cpu_buttons : function() {
		var elements = document.getElementsByName("master_cpus_button");
		var length = elements.length;
		var cpus = this.get('content').objectAt(this.get('project_index')).get('cpu_choices');
		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('master_cpu_selection') != 0) {
				var choice = document.getElementById("master_cpus_".concat(this.get('master_cpu_selection')));
				choice.style.color = "white";
			}
			if (this.get('slaves_cpu_selection') == 0) {
				var slaves_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
			} else {
				var slaves_cpu = this.get('slaves_cpu_selection');
			}
			if (cpus[i] > (this.get('content').objectAt(this.get('project_index')).get('cpu_av') - slaves_cpu * (this.size_of_cluster() - 1) )) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){			
			if (elements[1].disabled == true) {
				this.set('vm_flav_master_Small_disabled', true);
			} else {
				this.set('vm_flav_master_Small_disabled', false);
			}
			if (elements[2].disabled == true) {
				this.set('vm_flav_master_Medium_disabled', true);
				this.set('vm_flav_master_Large_disabled', true);
			} else {
				this.set('vm_flav_master_Medium_disabled', false);
				this.set('vm_flav_master_Large_disabled', false);
			}
		}

		var elements = document.getElementsByName("slaves_cpus_button");
		var length = elements.length;
		var cpus = this.get('content').objectAt(this.get('project_index')).get('cpu_choices');

		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('slaves_cpu_selection') != 0) {
				var choice = document.getElementById("slaves_cpus_".concat(this.get('slaves_cpu_selection')));
				choice.style.color = "white";
			}
			if (this.get('master_cpu_selection') == 0) {
				var master_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
			} else {
				var master_cpu = this.get('master_cpu_selection');
			}
			if (cpus[i] * (this.size_of_cluster() - 1) > (this.get('content').objectAt(this.get('project_index')).get('cpu_av') - master_cpu)) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){
			if (elements[1].disabled == true) {
				this.set('vm_flav_slave_Small_disabled', true);
			} else {
				this.set('vm_flav_slave_Small_disabled', false);
			}
			if (elements[2].disabled == true) {
				this.set('vm_flav_slave_Medium_disabled', true);
				this.set('vm_flav_slave_Large_disabled', true);
			} else {
				this.set('vm_flav_slave_Medium_disabled', false);
				this.set('vm_flav_slave_Large_disabled', false);
			}
		}
	},

	// Functionality about coloring of the ram buttons and enable-disable responding to user events
	// First, remove colors from all ram buttons and then color the role's(master/slaves) selection
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available ram, then disable the selected role button.
	ram_buttons : function() {

		var elements = document.getElementsByName("master_ram_button");
		var length = elements.length;
		var ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices');

		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('master_ram_selection') != 0) {
				var choice = document.getElementById("master_ram_".concat(this.get('master_ram_selection')));
				choice.style.color = "white";
			}
			if (this.get('slaves_ram_selection') == 0) {
				var slaves_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var slaves_ram = this.get('slaves_ram_selection');
			}
			if (ram[i] > (this.get('content').objectAt(this.get('project_index')).get('ram_av') - slaves_ram * (this.size_of_cluster() - 1) )) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){
			if (elements[2].disabled == true) {
				this.set('vm_flav_master_Small_disabled', true);
				this.set('vm_flav_master_Medium_disabled', true);
			}
			if (elements[3].disabled == true) {
				this.set('vm_flav_master_Large_disabled', true);
			}		
		}

		var elements = document.getElementsByName("slaves_ram_button");
		var length = elements.length;
		var ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices');

		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('slaves_ram_selection') != 0) {
				var choice = document.getElementById("slaves_ram_".concat(this.get('slaves_ram_selection')));
				choice.style.color = "white";
			}
			if (this.get('master_ram_selection') == 0) {
				var master_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var master_ram = this.get('master_ram_selection');
			}
			if (ram[i] * (this.size_of_cluster() - 1) > (this.get('content').objectAt(this.get('project_index')).get('ram_av') - master_ram)) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){
			if (elements[2].disabled == true) {
				this.set('vm_flav_slave_Small_disabled', true);
				this.set('vm_flav_slave_Medium_disabled', true);
			}
			if (elements[3].disabled == true) {
				this.set('vm_flav_slave_Large_disabled', true);
			}	
		}
	},

	// Functionality about coloring of the disk size buttons and enable-disable responding to user events
	// First, remove colors from all disk size buttons and then color the role's(master/slaves) selection
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available disk size, then disable the selected role button.
	disk_buttons : function() {
		var elements = document.getElementsByName("master_disk_button");
		var length = elements.length;
		var disks = this.get('content').objectAt(this.get('project_index')).get('disk_choices');

		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('master_disk_selection') != 0) {
				var choice = document.getElementById("master_disk_".concat(this.get('master_disk_selection')));
				choice.style.color = "white";
			}
			if (this.get('slaves_disk_selection') == 0) {
				var slaves_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var slaves_disk = this.get('slaves_disk_selection');
			}
			if (disks[i] > (this.get('content').objectAt(this.get('project_index')).get('disk_av') - slaves_disk * (this.size_of_cluster() - 1) )) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){
			if (elements[1].disabled == true) {
				this.set('vm_flav_master_Small_disabled', true);
			}
			if (elements[2].disabled == true) {
				this.set('vm_flav_master_Medium_disabled', true);
			}
			if (elements[3].disabled == true) {
				this.set('vm_flav_master_Large_disabled', true);
			}
		}

		var elements = document.getElementsByName("slaves_disk_button");
		var length = elements.length;
		var disks = this.get('content').objectAt(this.get('project_index')).get('disk_choices');

		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			if (this.get('slaves_disk_selection') != 0) {
				var choice = document.getElementById("slaves_disk_".concat(this.get('slaves_disk_selection')));
				choice.style.color = "white";
			}
			if (this.get('master_disk_selection') == 0) {
				var master_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var master_disk = this.get('master_disk_selection');
			}
			if (disks[i] * (this.size_of_cluster() - 1) > (this.get('content').objectAt(this.get('project_index')).get('disk_av') - master_disk)) {
				elements[i].disabled = true;
			} else {
				elements[i].disabled = false;
			}
		}
		if (length != 0){
			if (elements[1].disabled == true) {
				this.set('vm_flav_slave_Small_disabled', true);
			}
			if (elements[2].disabled == true) {
				this.set('vm_flav_slave_Medium_disabled', true);
			}
			if (elements[3].disabled == true) {
				this.set('vm_flav_slave_Large_disabled', true);
			}
		}
	},

    reverse_storage_lookup : function(){
        var storage_lookup = this.get('AppSettings').filterBy('section','Cyclades').filterBy('property_name','Storage');
        return JSON.parse(storage_lookup[0].get('property_value'));
    }.property(),
	// Functionality about storage buttons being colored when user selects one of them
	storage_buttons : function() {
		var elements = document.getElementsByName("storage_button");
		var length = elements.length;
		if (length == 1) {
          elements[0].style.color = "white";
          this.set('disk_temp',elements[0].value);
         }
		else{
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
			if (this.get('disk_temp') != '') {
					var choice = document.getElementById(this.get('disk_temp'));
					choice.style.color = "white";
				}
			}
	
			var elements = document.getElementsByName("storage_button");
			var length = elements.length;
			var disks = this.get('content').objectAt(this.get('project_index')).get('disk_template');
			for (var i = 0; i < length; i++) {
				elements[i].disabled = false;
			}
		}
	},

	// Function which call each button function
	buttons : function() {
		var insufficient_net_or_ip = !(Ember.isBlank(this.get('alert_mes_network')) && Ember.isBlank(this.get('alert_mes_float_ip')));
		if (!insufficient_net_or_ip){
			this.get('disable_controls')(false);
		}
		this.cpu_buttons();
		this.ram_buttons();
		this.disk_buttons();
		this.storage_buttons();
		this.vm_flavor_buttons();
		if (insufficient_net_or_ip){
			this.get('disable_controls')(true);
		}
		return insufficient_net_or_ip;
	},
	
	// Function which make the size of cluster equal or greater than minimum cluster
	size_of_cluster : function() {
		if ((Ember.isEmpty(this.get('cluster_size'))) || (this.get('cluster_size') === 0)) {
			this.set('cluster_size_var', 2);
		} else {
			this.set('cluster_size_var', this.get('cluster_size'));
		}
		return this.get('cluster_size_var');
	},
	
	// Reset project variables
	reset_project : function() {
		this.set('project_index', 0);
		this.set('project_current', '');
		this.set('project_name', '');
		this.set('project_details', '');		
	},
	
	// Reset variables after logout
	reset_variables : function() {
		this.set('cluster_size', 0);
		this.set('cluster_size_var', 0);
		this.set('master_cpu_selection', 0);
		this.set('slaves_cpu_selection', 0);
		this.set('master_ram_selection', 0);
		this.set('slaves_ram_selection', 0);
		this.set('master_disk_selection', 0);
		this.set('slaves_disk_selection', 0);
		this.set('cluster_name', '');
		this.set('operating_system', 'Debian Base');
		this.set('disk_temp', '');
		this.set('vm_flavor_selection_master', '');
		this.set('vm_flavor_selection_slaves', '');
		this.set('message', '');
		this.set('replication_factor', '');		
		this.set('dfs_blocksize', '');
		this.set('hue_message', '');
		this.set('workflow_filter', false);
		this.set('admin_password', '');
		this.init_alerts();
	},
	// initialize alert messages
	init_alerts : function() {
		this.set('alert_mes_master_cpu', '');
		this.set('alert_mes_master_ram', '');
		this.set('alert_mes_master_disk', '');
		this.set('alert_mes_slaves_cpu', '');
		this.set('alert_mes_slaves_ram', '');
		this.set('alert_mes_slaves_disk', '');
		this.set('alert_mes_disk_template', '');
		this.set('alert_mes_cluster_name', '');
		this.set('alert_mes_cluster_size', '');
		this.set('alert_mes_replication_factor', '');
		this.set('alert_mes_dfs_blocksize', '');
		this.set('warning_mes_replication_factor', '');
		this.set('warning_mes_dfs_blocksize', '');
		this.set('alert_missing_input_admin_password', '');
		
	},
	
	replication_factor_change : function(){
		if (((this.get('replication_factor') == this.get('default_replication_factor'))&&(this.get('cluster_size') != 2)) || ((this.get('replication_factor') == '1') && (this.get('cluster_size') == 2)) || (this.get('replication_factor')=='')){
			this.set('warning_mes_replication_factor', '');
		}
		else {
			this.set('warning_mes_replication_factor', 'Value differs from default');
		}
		return this.get('warning_mes_replication_factor');
	}.property('replication_factor','cluster_size'),
	

	dfs_blocksize_change : function(){
		if ((this.get('dfs_blocksize') == this.get('default_dfs_blocksize')) || (this.get('dfs_blocksize')=='')){
			this.set('warning_mes_dfs_blocksize', '');
		}
		else {
			this.set('warning_mes_dfs_blocksize', 'Value differs from default');	
		}
		return this.get('warning_mes_dfs_blocksize');
	}.property('dfs_blocksize'),
	
	image_name : function(){
		return this.get('operating_system');
	}.property('operating_system','project_details'),
	
	version_message : function(){
		var that = this;
        Ember.run.later(function() {
            var selected = $('#os_systems').val();
            if (Ember.isBlank(selected) || (selected == that.get('workflow_filter_empty'))) {
                that.set('info_popover_visible', false);
            } else {
                that.set('info_popover_visible', true);
            }         
        }, 500);
        var image_name = this.get('image_name');
        var arr_images = this.get('orkaImages');
        var popover_data = {};
        for ( i = 0; i < arr_images.length; i++) {
            if (arr_images.objectAt(i).get('image_name') == image_name) {
                for ( j = 0; j < arr_images.objectAt(i).get('image_components').length; j++) {
                    popover_data[arr_images.objectAt(i).get('image_components').objectAt(j).name] = arr_images.objectAt(i).get('image_components').objectAt(j).property['version'];
                }
                break;
            }
        }
        var msg = '';
        for (key in popover_data) {
            msg = '%@<b>%@</b>: <span class="text text-info">%@</span><br>'.fmt(msg, key, popover_data[key]);
        }
        return msg; 
	}.property('image_name'),
	
	message_hue_login : function(){
		this.get('controllers.clusterManagement').send('help_hue_login', this.get('operating_system'));
		if (this.get('hue_message') === 'CDH'){
			var msg = {'msg_type':'warning','msg_text':'IMPORTANT: First login in Hue browser with username: hdfs and password: ' + this.get('admin_password')};
			this.get('controllers.userWelcome').send('addMessage',msg);
		} else if (this.get('hue_message') === 'HUE'){
			var msg = {'msg_type':'warning','msg_text':'IMPORTANT: First login in Hue browser with username: hduser and password: ' + this.get('admin_password')};
			this.get('controllers.userWelcome').send('addMessage',msg);
		}
	},

	actions : {
		// action to generate random password for hue superuser
		admin_pass_generate : function(){
            this.set('admin_password',PassGen.generate(12));
            this.send('admin_pass_select');
        },
        admin_pass_select : function(){
            if (!Ember.isEmpty(this.get('admin_password'))){
                Ember.run.later(function(){$('#id_hue_admin_pass').select();},100);
                this.set('alert_missing_input_admin_password', '');           
            }
        },
		// action to focus project selection view
		focus_project_selection : function(){
			$('#project_id').focus();
		},
		// action to reset hdfs configuration parameters in default values
		default_hdfs_configuration : function(){
			this.set('replication_factor', this.get('default_replication_factor'));
			this.set('dfs_blocksize', this.get('default_dfs_blocksize'));
		},
		// action to apply last cluster configuration
		// trigger when the corresponding button is pressed
		applyLastCluster : function() {					
			if (!Ember.isEmpty(this.get('last_cluster'))){
				// find and select the last project
				var projects = [];
				this.set('workflow_filter', false);
				projects = this.get('projects_av');
				var length = projects.length;
				for (var i = 0; i < length; i++) {
					// check based on the name of the project (at screen we have both project name and quotas)
					if (projects.objectAt(i).string.lastIndexOf(clusterdata.project_name) > 0) {
						this.set('selected_project', projects.objectAt(i));
						break;
					}
				}
				// select/set the remaining of the last configurations						
				var self = this;
				Ember.run.later (function() {	
					self.set('last_cluster_conf_checked', true);	
					if ((clusterdata.cluster_size <= (self.get('max_cluster_size_av').length+1)) 
					&& ((clusterdata.cpu_master+(clusterdata.cpu_slaves*(clusterdata.cluster_size-1)))
						<= self.get('cpu_available')+self.get('master_cpu_selection')+self.get('slaves_cpu_selection')*(self.size_of_cluster()-1)) 
					&& ((clusterdata.ram_master+(clusterdata.ram_slaves*(clusterdata.cluster_size-1)))
						<= self.get('ram_available')+self.get('master_ram_selection')+self.get('slaves_ram_selection')*(self.size_of_cluster()-1))
					&& ((clusterdata.disk_master+(clusterdata.disk_slaves*(clusterdata.cluster_size-1)))
						<= self.get('disk_available')+self.get('master_disk_selection')+self.get('slaves_disk_selection')*(self.size_of_cluster()-1)))
					{
						self.set('alert_mes_last_conf', '');
						self.set('selected_image', clusterdata.os_image);
						self.set('cluster_size', clusterdata.cluster_size);
						self.set('disk_template_selection', self.get('reverse_storage_lookup')[clusterdata.disk_template], "storage_button");
						self.set('master_cpu_selection', clusterdata.cpu_master);
						self.set('slaves_cpu_selection', clusterdata.cpu_slaves);
						self.set('master_ram_selection', clusterdata.ram_master);
						self.set('slaves_ram_selection', clusterdata.ram_slaves);
						self.set('master_disk_selection', clusterdata.disk_master);
						self.set('slaves_disk_selection', clusterdata.disk_slaves);	
						self.message_hue_login();
					}
					else{
						self.set('alert_mes_last_conf', 'Lack of available resources.');
						self.reset_variables();
						self.reset_project();
						self.set('last_cluster_conf_checked', false);
					}				
				}, 1000);
			}			
		
		},
		// action triggered when entering the create cluster
		// find last cluster configuration for this user
		findLastCluster : function() {
			this.set('alert_mes_last_conf', '');
			this.set('last_conf_message', '');
			this.set('last_cluster', '');
			
			var self = this;
			var store = this.store;
			store.fetch('user', 1).then(function(user) {
				
				var clusters = user.get('clusters');
				var length = clusters.get('length');
				if (length > 0) {
					var last_date = null;
					if ((clusters.objectAt(0).get('cluster_status') == 1) || (clusters.objectAt(0).get('cluster_status') == 2)) {
						last_date = clusters.objectAt(0).get('action_date');
						self.set('last_cluster', clusters.objectAt(0));
					}
					for (var i = 1; i < length; i++) {
						if ((clusters.objectAt(i).get('cluster_status') == 1) || (clusters.objectAt(i).get('cluster_status') == 2)) {
							if ((last_date==null) || (clusters.objectAt(i).get('action_date') > last_date)) {
								last_date = clusters.objectAt(i).get('action_date');
								self.set('last_cluster', clusters.objectAt(i));
							}
						}
					}
				}
				
				if (!Ember.isEmpty(self.get('last_cluster'))){
					clusterdata = self.get('last_cluster').get('data');
					var label = '<b>Projects</b>: <span class="text text-info">' + clusterdata.project_name + '</span>'
					+ '<br><b>Available Images</b>: <span class="text text-info">' + clusterdata.os_image + '</span>'
					+ '<br><b>Cluster Size</b>: <span class="text text-info">' + clusterdata.cluster_size + '</span>'
					+ '<br><b>Storage</b>: <span class="text text-info">' + self.get('reverse_storage_lookup')[clusterdata.disk_template] + '</span>'
					+ '<br><b>Master CPUs</b>: <span class="text text-info">' + clusterdata.cpu_master + '</span>'
					+ '<br><b>Master RAM</b>: <span class="text text-info">' + clusterdata.ram_master + '</span>'
					+ '<br><b>Master Disk Size</b>: <span class="text text-info">' + clusterdata.disk_master + '</span>'
					+ '<br><b>Slaves CPUs</b>: <span class="text text-info">' + clusterdata.cpu_slaves + '</span>'
					+ '<br><b>Slaves RAM</b>: <span class="text text-info">' + clusterdata.ram_slaves + '</span>'
					+ '<br><b>Slaves Disk Size</b>: <span class="text text-info">' + clusterdata.disk_slaves + '</span>';
	
					self.set('last_conf_message', label);
				}
			}, function(reason) {
				console.log(reason.message);
			});
		},	
		vm_flavor_selection : function(value, name) {
			if (name == "vm_flavor_button_master") {
				this.set('vm_flavor_selection_master', value);
				if (value == "Small") {
					this.set('master_cpu_selection', this.get('flavor_settings')['Small']['cpu']);
				    this.set('master_ram_selection', this.get('flavor_settings')['Small']['ram']);
				    this.set('master_disk_selection', this.get('flavor_settings')['Small']['disk']);
				} 				
				if (value == "Medium") {
					this.set('master_cpu_selection', this.get('flavor_settings')['Medium']['cpu']);
				    this.set('master_ram_selection', this.get('flavor_settings')['Medium']['ram']);
				    this.set('master_disk_selection', this.get('flavor_settings')['Medium']['disk']);
				}
				if (value == "Large") {
					this.set('master_cpu_selection', this.get('flavor_settings')['Large']['cpu']);
					this.set('master_ram_selection', this.get('flavor_settings')['Large']['ram']);
					this.set('master_disk_selection', this.get('flavor_settings')['Large']['disk']);
				}
			}
			if (name == "vm_flavor_button_slaves") {
				this.set('vm_flavor_selection_slaves', value);
				if (value == "Small") {
					this.set('slaves_cpu_selection', this.get('flavor_settings')['Small']['cpu']);
					this.set('slaves_ram_selection', this.get('flavor_settings')['Small']['ram']);
					this.set('slaves_disk_selection', this.get('flavor_settings')['Small']['disk']);
				}
				if (value == "Medium") {
					this.set('slaves_cpu_selection', this.get('flavor_settings')['Medium']['cpu']);
					this.set('slaves_ram_selection', this.get('flavor_settings')['Medium']['ram']);
					this.set('slaves_disk_selection', this.get('flavor_settings')['Medium']['disk']);
				}
				if (value == "Large") {				
					this.set('slaves_cpu_selection', this.get('flavor_settings')['Large']['cpu']);				
					this.set('slaves_ram_selection', this.get('flavor_settings')['Large']['ram']);				
					this.set('slaves_disk_selection', this.get('flavor_settings')['Large']['disk']);	
				}
			}			
		},

		// When a cpu button is clicked, the selected role's cpu selection takes the corresponding value
		cpu_selection : function(value, name) {
			if (name == "master_cpus_button") {
				// remove alert message
				this.set('alert_mes_master_cpu', '');
				if (this.get('slaves_cpu_selection') == 0) {
					var slaves_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
				} else {
					var slaves_cpu = this.get('slaves_cpu_selection');
				}
				if (value <= (this.get('content').objectAt(this.get('project_index')).get('cpu_av') - slaves_cpu * (this.size_of_cluster() - 1) )) {
					this.set('master_cpu_selection', value);
				}
			}
			if (name == "slaves_cpus_button") {
				// remove alert message
				this.set('alert_mes_slaves_cpu', '');
				if (this.get('master_cpu_selection') == 0) {
					var master_cpu = this.get('content').objectAt(this.get('project_index')).get('cpu_choices')[0];
				} else {
					var master_cpu = this.get('master_cpu_selection');
				}
				if (value * (this.size_of_cluster() - 1) <= (this.get('content').objectAt(this.get('project_index')).get('cpu_av') - master_cpu)) {
					this.set('slaves_cpu_selection', value);
				}
			}
		},

		// When a ram button is clicked, the selected role's ram selection takes the corresponding value
		ram_selection : function(value, name) {
			if (this.get('master_ram_selection') == 0) {
				var master_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var master_ram = this.get('master_ram_selection');
			}
			if (this.get('slaves_ram_selection') == 0) {
				var slaves_ram = this.get('content').objectAt(this.get('project_index')).get('ram_choices')[0];
			} else {
				var slaves_ram = this.get('slaves_ram_selection');
			}

			if (name == "master_ram_button") {
				// remove alert message
				this.set('alert_mes_master_ram', '');
				if (value <= (this.get('content').objectAt(this.get('project_index')).get('ram_av') - slaves_ram * (this.size_of_cluster() - 1) )) {
					this.set('master_ram_selection', value);
				}
			}
			if (name == "slaves_ram_button") {
				// remove alert message
				this.set('alert_mes_slaves_ram', '');
				if (value * (this.size_of_cluster() - 1) <= (this.get('content').objectAt(this.get('project_index')).get('ram_av') - master_ram)) {
					this.set('slaves_ram_selection', value);
				}
			}
		},

		// When a disk button is clicked, the selected role's disk selection takes the corresponding value
		disk_selection : function(value, name) {		
			if (this.get('master_disk_selection') == 0) {
				var master_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var master_disk = this.get('master_disk_selection');
			}
			if (this.get('slaves_disk_selection') == 0) {
				var slaves_disk = this.get('content').objectAt(this.get('project_index')).get('disk_choices')[0];
			} else {
				var slaves_disk = this.get('slaves_disk_selection');
			}

			if (name == "master_disk_button") {
				// remove alert message
				this.set('alert_mes_master_disk', '');
				if (value <= (this.get('content').objectAt(this.get('project_index')).get('disk_av') - slaves_disk * (this.size_of_cluster() - 1) )) {
					this.set('master_disk_selection', value);
				}
			}
			if (name == "slaves_disk_button") {
				// remove alert message
				this.set('alert_mes_slaves_disk', '');
				if (value * (this.size_of_cluster() - 1) <= (this.get('content').objectAt(this.get('project_index')).get('disk_av') - master_disk)) {
					this.set('slaves_disk_selection', value);
				}
			}
		},

		// When a storage button is clicked, the selected role's storage selection takes the corresponding value
		disk_template_selection : function(value, name) {
			this.set('disk_temp', value);

			// if "Standard" is selected, check disk sizes 
			// disk sizes for master/slaves should be <=20
			if(value == 'Standard')
			{
				var length = this.get('content').objectAt(this.get('project_index'))
								.get('disk_choices').length;
												
				// if master disk selection invalid
				if(this.get('master_disk_selection') > 20)
				{
					// then select the highest allowed value
					for (var i = length-1; i >= 0; i--) {
						var value = this.get('content').objectAt(this.get('project_index'))
						.get('disk_choices')[i];
						
						if( value <= 20)
						{
							this.send('disk_selection', value, "master_disk_button");
							break;
						}					
					}	
				}
				// if slaves disk selection invalid
				if(this.get('slaves_disk_selection') > 20)
				{
					// then select the highest allowed value
					for (var i = length-1; i >= 0; i--) {
						var value = this.get('content').objectAt(this.get('project_index'))
						.get('disk_choices')[i];
						
						if( value <= 20)
						{
							this.send('disk_selection', value, "slaves_disk_button");
							break;
						}					
					}	
				}				
			}
		},
		// Cancel action when in create cluster -> redirect to user's welcome screen
		cancel : function() {
		    var that = this;
			// reset variables();
			this.reset_variables();
			this.reset_project();
			this.get('controllers.userWelcome').send('setActiveTab','clusters');
			// redirect to welcome
			Ember.run.next(function(){that.transitionToRoute('user.welcome');});
		},
		// when create cluster button is pressed
		// go_to_create action is triggered
		go_to_create : function() {
			$options = {
				title : 'Redirect to welcome page and start building cluster',
				fontColor : false,
				bgColor : 'transparent',
				size : 32,
				isOnly : true,
				bgOpacity : 1.0,
				imgUrl : DJANGO_STATIC_URL + "images/loading[size].gif",
				onShow : function() {
					$.loader.shown = true;
					$('.loading_wrp').find('span').addClass('text-primary big strong');
				},
				onClose : function() {
					$.loader.shown = false;
				}
			};
			//$('#next').loader($options); // on $('selector')

			this.init_alerts();	
			if ((this.get('replication_factor')=='') || (this.get('replication_factor')==null)){
				if (this.get('cluster_size')==2){
					this.set('replication_factor', 1);
				}
				else {
					this.set('replication_factor', this.get('default_replication_factor'));
				}				
			}
			if ((this.get('dfs_blocksize')=='') || (this.get('dfs_blocksize')==null)){
				this.set('dfs_blocksize', this.get('default_dfs_blocksize'));
			}
			if (!Ember.isBlank(this.get('alert_mes_network')) || !Ember.isBlank(this.get('alert_mes_float_ip'))){
				var elem = $('#id_project_selection');
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if ((this.get('admin_password') == '') && this.get('hue_in_image')) {
				this.set('alert_missing_input_admin_password', 'Please type in or generate an admin password. Copy it for first time login.');
				// scroll to message
				var elem = document.getElementById("common_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if ((!(/^[^\W_]{8,}$/gi.test(this.get('admin_password')))) && this.get('hue_in_image')) {
				this.set('alert_missing_input_admin_password', 'Password should be at least 8 characters and contain only letters and numbers.');
				// scroll to message
				var elem = document.getElementById("common_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if ((this.get('cluster_size') === null) || (this.get('cluster_size') === undefined) || (this.get('cluster_size') === 0)) {
				this.set('alert_mes_cluster_size', 'Please select cluster size');
				// scroll to message
				var elem = document.getElementById("common_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('master_cpu_selection') == 0) {
				this.set('alert_mes_master_cpu', 'Please select master cpu');
				// scroll to message
				var elem = document.getElementById("master_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('master_ram_selection') == 0) {
				this.set('alert_mes_master_ram', 'Please select master ram');
				// scroll to message
				var elem = document.getElementById("master_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('master_disk_selection') == 0) {
				this.set('alert_mes_master_disk', 'Please select master disk');
				// scroll to message
				var elem = document.getElementById("master_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('slaves_cpu_selection') == 0) {
				this.set('alert_mes_slaves_cpu', 'Please select slaves cpu');
				// scroll to message
				var elem = document.getElementById("slaves_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('slaves_ram_selection') == 0) {
				this.set('alert_mes_slaves_ram', 'Please select slaves ram');
				// scroll to message
				var elem = document.getElementById("slaves_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('slaves_disk_selection') == 0) {
				this.set('alert_mes_slaves_disk', 'Please select slaves disk');
				// scroll to message
				var elem = document.getElementById("slaves_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			} else if (this.get('disk_temp') == '') {
				this.set('alert_mes_disk_template', 'Please select disk template');
				// scroll to message
				var elem = document.getElementById("common_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);	
			} else if (this.get('cluster_name') == '') {
				this.set('alert_mes_cluster_name', 'Please input cluster name');
				// scroll to message
				var elem = document.getElementById("common_settings");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			}
			else if (isNaN(parseInt(this.get('replication_factor')))){
				this.set('alert_mes_replication_factor', 'Replication_factor is an integer');
				var elem = document.getElementById("hdfs_configuration");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			}
			else if ((parseInt(this.get('replication_factor')) > (this.get('cluster_size')-1)) || (parseInt(this.get('replication_factor')) <= 0)){
				this.set('alert_mes_replication_factor', 'Replication_factor must be positive and not greater than the number of slaves');
				var elem = document.getElementById("hdfs_configuration");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);					
			}
			else if (isNaN(parseInt(this.get('dfs_blocksize')))){
				this.set('alert_mes_dfs_blocksize', 'Blocksize is an integer');
				var elem = document.getElementById("hdfs_configuration");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);
			}
			else if (parseInt(this.get('dfs_blocksize')) <= 0){
				this.set('alert_mes_dfs_blocksize', 'Blocksize must be positive');
				var elem = document.getElementById("hdfs_configuration");
				window.scrollTo(elem.offsetLeft, elem.offsetTop);					
			}		
			else {
				$.loader.open($options);
				//body
				// check if everything is allowed
				if ((this.get('total_cpu_selection') <= this.get('content').objectAt(this.get('project_index')).get('cpu_av')) 
					&& (this.get('total_ram_selection') <= this.get('content').objectAt(this.get('project_index')).get('ram_av')) 
					&& (this.get('total_disk_selection') <= this.get('content').objectAt(this.get('project_index')).get('disk_av'))
					&& (this.get('content').objectAt(this.get('project_index')).get('net_av')>0)
					&& (this.get('content').objectAt(this.get('project_index')).get('floatip_av')>0) ) {
					var self = this;
					// PUT request
					if ((this.get('ssh_key_selection')=='') || (this.get('ssh_key_selection')==null)){
						this.set('ssh_key_selection', 'no_ssh_key_selected');
					}
					// unload cached records
					this.store.unloadAll('clusterchoice');
					var cluster_selection = this.store.push('clusterchoice', {
						// set the clusterchoice model with the user choices
						'id' : 1,
						'project_name' : self.get('project_name'),
						'cluster_name' : self.get('cluster_name'),
						'cluster_size' : self.get('cluster_size'),
						'cpu_master' : self.get('master_cpu_selection'),
						'ram_master' : self.get('master_ram_selection'),
						'disk_master' : self.get('master_disk_selection'),
						'cpu_slaves' : self.get('slaves_cpu_selection'),
						'ram_slaves' : self.get('slaves_ram_selection'),
						'disk_slaves' : self.get('slaves_disk_selection'),
						'disk_template' : self.get('disk_temp'),
						'os_choice' : self.get('operating_system'),
						'ssh_key_selection' : self.get('ssh_key_selection'),
						'replication_factor' : self.get('replication_factor'),
						'dfs_blocksize': self.get('dfs_blocksize'),
						'admin_password': self.get('admin_password')
					}).save();
					
					this.message_hue_login();
					
					cluster_selection.then(function(clusterchoice) {
						// Set the response to user's create cluster click when put succeeds.
						$.loader.close(true);
                        var message = clusterchoice.get('data').message || "";
                        self.set('message', message);
                        if (!Ember.isBlank(message)){
                        	var msg = {'msg_type':'danger','msg_text':message};
                        	self.get('controllers.userWelcome').send('addMessage',msg);
                        }
						self.set('controllers.userWelcome.create_cluster_start', true);
						self.store.fetch('user', 1).then(function(user){
						    self.get('controllers.userWelcome').send('setActiveTab','clusters');
							self.transitionToRoute('user.welcome');
						},function(reason){
							console.log(reason.message);
						});
					}, function(reason) {
						// Set the response to user's create cluster click when put fails.
						console.log(reason.message);
						$.loader.close(true);
						self.set('message', reason.message);
						if (!Ember.isBlank(reason.message)){
							var msg = {'msg_type':'danger','msg_text':reason.message};
                        	self.get('controllers.userWelcome').send('addMessage',msg);
						}
						self.set('controllers.userWelcome.create_cluster_start', false);
						self.store.fetch('user', 1);
					});
				} else {
					alert('Requested resources unavailable!');
					$.loader.close(true);
				}
			}
		}
	}
});
