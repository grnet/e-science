// Cluster/create controller
App.ClusterCreateController = Ember.Controller.extend({

	// Initialization phase
	master_enabled : false, 	// Variable checking if master button is selected
	slaves_enabled : false, 	// Variable checking if slaves button is selected	
	cpu_Not_Allow : true, 		// Disabling all cpu buttons (master or slaves must be selected first for the buttons to be enabled)
	mem_Not_Allow : true, 		// Disabling all ram buttons (master or slaves must be selected first for the buttons to be enabled)
	disk_Not_Allow : true, 		// Disabling all disk buttons (master or slaves must be selected first for the buttons to be enabled)
	storage_Not_Allow : true, 	// Disabling all storage buttons (master or slaves must be selected first for the buttons to be enabled)
	cluster_size : 2, 		// Initial cluster size
	master_color : 'lightblue', 	// Initial colour of master button 
	slaves_color : 'lightblue', 	// Initial colour of slaves button
	master_cpu_selection : 0, 	// Initial master_cpu_selection, appears in master cpu summary
	slaves_cpu_selection : 0, 	// Initial slaves_cpu_selection, appears in slaves cpu summary
	master_mem_selection : 0, 	// Initial master_mem_selection, appears in master ram summary
	slaves_mem_selection : 0, 	// Initial slaves_mem_selection, appears in slaves ram summary
	master_disk_selection : 0, 	// Initial master_disk_selection, appears in master disk summary
	slaves_disk_selection : 0, 	// Initial slaves_disk_selection, appears in slaves disk summary
	cluster_name : '', 		// Initial cluster name, null
	operating_system : 'Debian Base', 	// Preselected OS
	disk_temp : 'ext_vlmc', 		// Initial storage selection, common for master and slaves

	
	// If cluster size is less than two, disable slaves option
	slaves_Not_Allow : function() {
		if (this.get('cluster_size') < 2) {
			this.set('slaves_mem_selection', 0);
			this.set('slaves_disk_selection', 0);
			this.set('slaves_cpu_selection', 0);
			this.set('master_color', 'lightgreen');
			this.set('slaves_color', 'lightgrey');
			this.set('master_enabled', true);
			this.set('slaves_enabled', false);
			this.buttons();
			return true;
		} else {
			return false;
		}
	}.property('cluster_size'),

	// The total cpus selected for the cluster
	total_cpu_selection : function() {
		return (this.get('master_cpu_selection') + this.get('slaves_cpu_selection') * (this.get('cluster_size') - 1));
	}.property('master_cpu_selection', 'slaves_cpu_selection', 'cluster_size'),

	// Computes the available cpu each time total_cpu_selection changes
	cpu_available : function() {
		var cpu_avail = this.get('content._data.cpu_av') - this.get('total_cpu_selection');
		if (cpu_avail < 0) {
			alert('The cluster size you selected with the current cpu choices exceed the cpu quota. You should lower the clustersize, change cpu values and select the clustersize again');
		} else {
			return cpu_avail;
		}
	}.property('total_cpu_selection'),
	
	// The total memory selected for the cluster
	total_mem_selection : function() {
		return (this.get('master_mem_selection') + this.get('slaves_mem_selection') * (this.get('cluster_size') - 1));
	}.property('master_mem_selection', 'slaves_mem_selection', 'cluster_size'),

	// Computes the available memory each time total_mem_selection changes
	mem_available : function() {
		mem_avail = this.get('content._data.mem_av') - this.get('total_mem_selection');
		if (mem_avail < 0) {
			alert('The cluster size you selected with the current ram choices exceed the ram quota. You should lower the clustersize, change ram values and select the clustersize again');
		} else {
			return mem_avail;
		}
	}.property('total_mem_selection'),
	
	// The total disk selected for the cluster
	total_disk_selection : function() {
		return (this.get('master_disk_selection') + this.get('slaves_disk_selection') * (this.get('cluster_size') - 1));
	}.property('master_disk_selection', 'slaves_disk_selection', 'cluster_size'),

	// Computes the available disk each time total_disk_selection changes
	disk_available : function() {
		disk_avail = this.get('content._data.disk_av') - this.get('total_disk_selection');
		if (disk_avail < 0) {
			alert('The cluster size you selected with the current disk choices exceed the disk quota. You should lower the clustersize, change disk values and select the clustersize again');
		} else {
			return disk_avail;
		}
	}.property('total_disk_selection'),

	// Computes the maximum vms that can be build with current flavor choices and return this to the drop down menu on index
	// If a flavor selection of a role(master/slaves) is 0, we assume that the role should be able to have at least the minimum option of the corresponding flavor
	// Available vms are limited by user quota. First, they are filtered with cpu limits, then with ram and finally with disk. The result is returned to the drop down menu on index
	max_cluster_size_av : function() {
		var length = this.get('content._data.vms_av').length;
		var max_cluster_size_limited_by_current_cpus = [];
		var max_cluster_size_limited_by_current_mems = [];
		var max_cluster_size_limited_by_current_disks = [];
		this.buttons();
		for (var i = 0; i < length; i++) {
			if (this.get('master_cpu_selection') == 0) {
				var master_cpu = this.get('content._data.cpu_choices')[0];
			} else {
				var master_cpu = this.get('master_cpu_selection');
			}
			if (this.get('slaves_cpu_selection') == 0) {
				var slaves_cpu = this.get('content._data.cpu_choices')[0];
			} else {
				var slaves_cpu = this.get('slaves_cpu_selection');
			}
			if ((this.get('content._data.cpu_av') - (master_cpu + ((this.get('content._data.vms_av')[i] - 1) * slaves_cpu))) < 0) {
				break;
			} else {
				for (var j = 0; j <= i; j++) {
					max_cluster_size_limited_by_current_cpus[j] = this.get('content._data.vms_av')[j];
				}
			}
		}
		length = max_cluster_size_limited_by_current_cpus.length;
		for ( i = 0; i < length; i++) {
			if (this.get('master_mem_selection') == 0) {
				var master_mem = this.get('content._data.mem_choices')[0];
			} else {
				var master_mem = this.get('master_mem_selection');
			}
			if (this.get('slaves_mem_selection') == 0) {
				var slaves_mem = this.get('content._data.mem_choices')[0];
			} else {
				var slaves_mem = this.get('slaves_mem_selection');
			}
			if ((this.get('content._data.mem_av') - (master_mem + ((max_cluster_size_limited_by_current_cpus[i] - 1) * slaves_mem))) < 0) {
				break;
			} else {
				for ( j = 0; j <= i; j++) {
					max_cluster_size_limited_by_current_mems[j] = max_cluster_size_limited_by_current_cpus[j];
				}
			}
		}
		length = max_cluster_size_limited_by_current_mems.length;
		for ( i = 0; i < length; i++) {
			if (this.get('slaves_disk_selection') == 0) {
				var slaves_disk = this.get('content._data.disk_choices')[0];
			} else {
				var slaves_disk = this.get('slaves_disk_selection');
			}
			if (this.get('master_disk_selection') == 0) {
				var master_disk = this.get('content._data.disk_choices')[0];
			} else {
				var master_disk = this.get('master_disk_selection');
			}
			if ((this.get('content._data.disk_av') - (master_disk + ((max_cluster_size_limited_by_current_mems[i] - 1) * slaves_disk))) < 0) {
				break;
			}
			for ( j = 0; j <= i; j++) {
				max_cluster_size_limited_by_current_disks[j] = max_cluster_size_limited_by_current_mems[j];
			}
		}
		return max_cluster_size_limited_by_current_disks;
	}.property('total_cpu_selection', 'total_mem_selection', 'total_disk_selection'),

	// Functionality about coloring of the cpu buttons and enable-disable responding to user events
	// First, remove colors from all cpu buttons and then color the role's(master/slaves) selection 
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available cpu, then disable the selected role button.
	cpu_buttons : function() {
		var elements = document.getElementsByName("cpu_button");
		var length = elements.length;
		var cpus = this.get('content._data.cpu_choices');
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_cpu_selection') != 0) {
					var choice = document.getElementById(this.get('master_cpu_selection'));
					choice.style.color = "red";
				}
				if (this.get('slaves_cpu_selection') == 0) {
					var slaves_cpu = this.get('content._data.cpu_choices')[0];
				} else {
					var slaves_cpu = this.get('slaves_cpu_selection');
				}
				if (cpus[i] > (this.get('content._data.cpu_av') - slaves_cpu * (this.get('cluster_size') - 1) )) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
		if (this.slaves_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('slaves_cpu_selection') != 0) {
					var choice = document.getElementById(this.get('slaves_cpu_selection'));
					choice.style.color = "red";
				}
				if (this.get('master_cpu_selection') == 0) {
					var master_cpu = this.get('content._data.cpu_choices')[0];
				} else {
					var master_cpu = this.get('master_cpu_selection');
				}
				if (cpus[i] * (this.get('cluster_size') - 1) > (this.get('content._data.cpu_av') - master_cpu)) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
	},

	// Functionality about coloring of the memory buttons and enable-disable responding to user events
	// First, remove colors from all memory buttons and then color the role's(master/slaves) selection 
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available memory, then disable the selected role button.
	memory_buttons : function() {
		var elements = document.getElementsByName("mem_button");
		var length = elements.length;
		var memories = this.get('content._data.mem_choices');
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_mem_selection') != 0) {
					var choice = document.getElementById(this.get('master_mem_selection'));
					choice.style.color = "red";
				}
				if (this.get('slaves_mem_selection') == 0) {
					var slaves_mem = this.get('content._data.mem_choices')[0];
				} else {
					var slaves_mem = this.get('slaves_mem_selection');
				}
				if (memories[i] > (this.get('content._data.mem_av') - slaves_mem * (this.get('cluster_size') - 1) )) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
		if (this.slaves_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('slaves_mem_selection') != 0) {
					var choice = document.getElementById(this.get('slaves_mem_selection'));
					choice.style.color = "red";
				}
				if (this.get('master_mem_selection') == 0) {
					var master_mem = this.get('content._data.mem_choices')[0];
				} else {
					var master_mem = this.get('master_mem_selection');
				}
				if (memories[i] * (this.get('cluster_size') - 1) > (this.get('content._data.mem_av') - master_mem)) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
	},

	// Functionality about coloring of the disk size buttons and enable-disable responding to user events
	// First, remove colors from all disk size buttons and then color the role's(master/slaves) selection 
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available disk size, then disable the selected role button.
	disk_buttons : function() {
		var elements = document.getElementsByName("disk_button");
		var length = elements.length;
		var disks = this.get('content._data.disk_choices');
		var last = disks.length;
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_disk_selection') != 0) {
					var choice = document.getElementById(this.get('master_disk_selection'));
					choice.style.color = "red";
				}
				if (this.get('slaves_disk_selection') == 0) {
					var slaves_disk = this.get('content._data.disk_choices')[0];
				} else {
					var slaves_disk = this.get('slaves_disk_selection');
				}
				if (disks[i] > (this.get('content._data.disk_av') - slaves_disk * (this.get('cluster_size') - 1) )) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
		if (this.slaves_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('slaves_disk_selection') != 0) {
					var choice = document.getElementById(this.get('slaves_disk_selection'));
					choice.style.color = "red";
				}
				if (this.get('master_disk_selection') == 0) {
					var master_disk = this.get('content._data.disk_choices')[0];
				} else {
					var master_disk = this.get('master_disk_selection');
				}
				if (disks[i] * (this.get('cluster_size') - 1) > (this.get('content._data.disk_av') - master_disk)) {
					elements[i].disabled = true;
				} else {
					elements[i].disabled = false;
				}
			}
		}
	},

	// Functionality about storage buttons being colored when user selects one of them
	storage_buttons : function() {
		var elements = document.getElementsByName("storage_button");
		var length = elements.length;
		var disks = this.get('content._data.disk_template');
		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			var choice = document.getElementById(this.get('disk_temp'));
			choice.style.color = "red";
		}
	},

	// Function which call each button function
	buttons : function() {
		this.cpu_buttons();
		this.memory_buttons();
		this.disk_buttons();
		this.storage_buttons();
	},
	// Reset variables after logout
	reset_variables : function() {
		this.set('master_enabled', false);
		this.set('slaves_enabled', false);
		this.set('cpu_Not_Allow', true);
		this.set('mem_Not_Allow', true);
		this.set('disk_Not_Allow', true);
		this.set('storage_Not_Allow', true);
		this.set('cluster_size', 2);
		this.set('master_color', 'lightblue');
		this.set('slaves_color', 'lightblue');
		this.set('master_cpu_selection', 0);
		this.set('slaves_cpu_selection', 0);
		this.set('master_mem_selection', 0);
		this.set('slaves_mem_selection', 0);
		this.set('master_disk_selection', 0);
		this.set('slaves_disk_selection', 0);
		this.set('cluster_name', '');
		this.set('operating_system', 'Debian Base');
		this.set('disk_temp', 'ext_vlmc');
	},
	actions : {

		// When a cpu button is clicked, the selected role's cpu selection takes the corresponding value
		cpu_selection : function(name) {
			if (this.master_enabled) {
				if (name <= (this.get('content._data.cpu_av') - this.get('slaves_cpu_selection') * (this.get('cluster_size') - 1) )) {
					this.set('master_cpu_selection', name);
				}
			}
			if (this.slaves_enabled) {
				if (name * (this.get('cluster_size') - 1) <= (this.get('content._data.cpu_av') - this.get('master_cpu_selection'))) {
					this.set('slaves_cpu_selection', name);
				}
			}
		},

		// When a memory button is clicked, the selected role's memory selection takes the corresponding value
		mem_selection : function(name) {
			if (this.master_enabled) {
				if (name <= (this.get('content._data.mem_av') - this.get('slaves_mem_selection') * (this.get('cluster_size') - 1) )) {
					this.set('master_mem_selection', name);
				}
			}
			if (this.slaves_enabled) {

				if (name * (this.get('cluster_size') - 1) <= (this.get('content._data.mem_av') - this.get('master_mem_selection'))) {
					this.set('slaves_mem_selection', name);
				}
			}
		},

		// When a disk button is clicked, the selected role's disk selection takes the corresponding value
		disk_selection : function(name) {
			if (this.master_enabled) {
				if (name <= (this.get('content._data.disk_av') - this.get('slaves_disk_selection') * (this.get('cluster_size') - 1) )) {
					this.set('master_disk_selection', name);
				}
			}
			if (this.slaves_enabled) {
				if (name * (this.get('cluster_size') - 1) <= (this.get('content._data.disk_av') - this.get('master_disk_selection'))) {
					this.set('slaves_disk_selection', name);
				}
			}
		},

		// When a storage button is clicked, the selected role's storage selection takes the corresponding value
		disk_template : function(name) {
			this.set('disk_temp', name);
			this.storage_buttons();
		},

		// When logout is clicked, starts transition to user logout route and home page screen
		logout : function() {
			// reset variables();
			this.reset_variables();
			// redirect to logout
			this.transitionTo('user.logout');
		},


		// When master button is clicked, disables the slave button accordingly and calls button function
		display_master : function() {
			this.set('master_color', 'lightgreen');
			this.set('slaves_color', 'lightgrey');
			this.set('master_enabled', true);
			this.set('slaves_enabled', false);
			this.buttons();
			this.set('storage_Not_Allow', false);
		},



		// When slaves button is clicked, disables the master button accordingly and calls button function
		display_slaves : function() {
			this.set('master_color', 'lightgrey');
			this.set('slaves_color', 'lightgreen');
			this.set('master_enabled', false);
			this.set('slaves_enabled', true);
			this.buttons();
			this.set('storage_Not_Allow', false);
		},

		// when next button is pressed
		// go_to_confirm action is triggered
		go_to_confirm : function() {
			// check that all fields are filled
			if (this.get('master_cpu_selection') == 0) {
				alert('Please select master cpu');
			} else if (this.get('master_mem_selection') == 0) {
				alert('Please select master memory');
			} else if (this.get('master_disk_selection') == 0) {
				alert('Please select master disk');
			} else if ((this.get('slaves_cpu_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves cpu');
			} else if ((this.get('slaves_mem_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves memory');
			} else if ((this.get('slaves_disk_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves disk');
			} else if (this.get('cluster_name') == '') {
				alert('Please input cluster name');
			} else {
				// check if everything is allowed
				if ((this.get('total_cpu_selection') <= this.get("content._data.cpu_av")) && (this.get('total_mem_selection') <= this.get("content._data.mem_av")) && (this.get('total_disk_selection') <= this.get("content._data.disk_av"))) {
					// redirect to confirm template
					this.transitionTo('cluster.confirm');
				} else {
					alert('Requested resources unavailable!');
				}
			}
		},
	},

	// Style for master button
	master_style : function() {
		return "background-color:" + this.get('master_color');
	}.property('master_color'),

	// Style for slaves button
	slaves_style : function() {
		return "background-color:" + this.get('slaves_color');
	}.property('slaves_color')
});
