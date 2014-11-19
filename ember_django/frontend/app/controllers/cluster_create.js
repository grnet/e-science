// Cluster/create controller
App.ClusterCreateController = Ember.Controller.extend({

	// Initialization phase
	master_cpus_Not_Allow : false, 		// Disabling all cpu buttons (master or slaves must be selected first for the buttons to be enabled)
	slaves_cpus_Not_Allow : false, 		// Disabling all cpu buttons (master or slaves must be selected first for the buttons to be enabled)
	master_ram_Not_Allow : false, 		// Disabling all ram buttons (master or slaves must be selected first for the buttons to be enabled)
	slaves_ram_Not_Allow : false, 		// Disabling all ram buttons (master or slaves must be selected first for the buttons to be enabled)
	master_disk_Not_Allow : false, 		// Disabling all disk buttons (master or slaves must be selected first for the buttons to be enabled)
	slaves_disk_Not_Allow : false, 		// Disabling all disk buttons (master or slaves must be selected first for the buttons to be enabled)
	storage_Not_Allow : false, 	// Disabling all storage buttons (master or slaves must be selected first for the buttons to be enabled)
	cluster_size : 0, 		// Initial cluster size
	master_cpu_selection : 0, 	// Initial master_cpu_selection, appears in master cpu summary
	slaves_cpu_selection : 0, 	// Initial slaves_cpu_selection, appears in slaves cpu summary
	master_ram_selection : 0, 	// Initial master_mem_selection, appears in master ram summary
	slaves_ram_selection : 0, 	// Initial slaves_mem_selection, appears in slaves ram summary
	master_disk_selection : 0, 	// Initial master_disk_selection, appears in master disk summary
	slaves_disk_selection : 0, 	// Initial slaves_disk_selection, appears in slaves disk summary
	cluster_name : '', 		// Initial cluster name, null
	operating_system : 'Debian Base', 	// Preselected OS
	disk_temp : 'ext_vlmc', 		// Initial storage selection, common for master and slaves
	message: '',
	alert_mes_master_cpu: '',
	alert_mes_master_ram: '',
	alert_mes_master_disk: '',
	alert_mes_slaves_cpu: '',
	alert_mes_slaves_ram: '',
	alert_mes_slaves_disk: '',
	alert_mes_cluster_name: '',
	// The total cpus selected for the cluster
	total_cpu_selection : function() {
		return (this.get('master_cpu_selection') + this.get('slaves_cpu_selection') * (this.size_of_cluster() - 1));
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
	total_ram_selection : function() {
		return (this.get('master_ram_selection') + this.get('slaves_ram_selection') * (this.size_of_cluster() - 1));
	}.property('master_ram_selection', 'slaves_ram_selection', 'cluster_size'),

	// Computes the available memory each time total_mem_selection changes
	ram_available : function() {
		ram_avail = this.get('content._data.mem_av') - this.get('total_ram_selection');
		if (ram_avail < 0) {
			alert('The cluster size you selected with the current ram choices exceed the ram quota. You should lower the clustersize, change ram values and select the clustersize again');
		} else {
			return ram_avail;
		}
	}.property('total_ram_selection'),
	
	// The total disk selected for the cluster
	total_disk_selection : function() {
		return (this.get('master_disk_selection') + this.get('slaves_disk_selection') * (this.size_of_cluster() - 1));
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
		for (var i = 1; i < length; i++) {
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
				for (var j = 0; j < i; j++) {
					max_cluster_size_limited_by_current_cpus[j] = this.get('content._data.vms_av')[j+1];
				}
			}
		}
		length = max_cluster_size_limited_by_current_cpus.length;
		for ( i = 0; i < length; i++) {
			if (this.get('master_ram_selection') == 0) {
				var master_ram = this.get('content._data.mem_choices')[0];
			} else {
				var master_ram = this.get('master_ram_selection');
			}
			if (this.get('slaves_ram_selection') == 0) {
				var slaves_ram = this.get('content._data.mem_choices')[0];
			} else {
				var slaves_ram = this.get('slaves_ram_selection');
			}
			if ((this.get('content._data.mem_av') - (master_ram + ((max_cluster_size_limited_by_current_cpus[i] - 1) * slaves_ram))) < 0) {
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
	}.property('total_cpu_selection', 'total_ram_selection', 'total_disk_selection'),

	// Functionality about coloring of the cpu buttons and enable-disable responding to user events
	// First, remove colors from all cpu buttons and then color the role's(master/slaves) selection 
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available cpu, then disable the selected role button.
	cpu_buttons : function() {
	    
	    var elements = document.getElementsByName("master_cpus_button");
	    var length = elements.length;
	    var cpus = this.get('content._data.cpu_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('master_cpu_selection') != 0) {
		    var choice = document.getElementById("master_cpus_".concat(this.get('master_cpu_selection')));
		    choice.style.color = "red";
		}
		if (this.get('slaves_cpu_selection') == 0) {
		    var slaves_cpu = this.get('content._data.cpu_choices')[0];
		} else {
		    var slaves_cpu = this.get('slaves_cpu_selection');
		}
		if (cpus[i] > (this.get('content._data.cpu_av') - slaves_cpu * (this.size_of_cluster() - 1) )) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
		}
	    }

	    var elements = document.getElementsByName("slaves_cpus_button");
	    var length = elements.length;
	    var cpus = this.get('content._data.cpu_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('slaves_cpu_selection') != 0) {
		    var choice = document.getElementById("slaves_cpus_".concat(this.get('slaves_cpu_selection')));
		    choice.style.color = "red";
		}
		if (this.get('master_cpu_selection') == 0) {
		    var master_cpu = this.get('content._data.cpu_choices')[0];
		} else {
		    var master_cpu = this.get('master_cpu_selection');
		}
		if (cpus[i] * (this.size_of_cluster() - 1) > (this.get('content._data.cpu_av') - master_cpu)) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
		}
	    }
	},

	// Functionality about coloring of the memory buttons and enable-disable responding to user events
	// First, remove colors from all memory buttons and then color the role's(master/slaves) selection 
	// Check all the possible combinations of selected role buttons with the unselected role's selection
	// (if selection is 0 we assume the minimum selection)
	// If the sum of them exceed the available memory, then disable the selected role button.
	memory_buttons : function() {
	  
	    var elements = document.getElementsByName("master_ram_button");
	    var length = elements.length;
	    var memories = this.get('content._data.mem_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('master_ram_selection') != 0) {
		    var choice = document.getElementById("master_ram_".concat(this.get('master_ram_selection')));
		    choice.style.color = "red";
		}
		if (this.get('slaves_ram_selection') == 0) {
		    var slaves_ram = this.get('content._data.mem_choices')[0];
		} else {
		    var slaves_ram = this.get('slaves_ram_selection');
		}
		if (memories[i] > (this.get('content._data.mem_av') - slaves_ram * (this.size_of_cluster() - 1) )) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
		}
	    }

    	    var elements = document.getElementsByName("slaves_ram_button");
	    var length = elements.length;
	    var memories = this.get('content._data.mem_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('slaves_ram_selection') != 0) {
		    var choice = document.getElementById("slaves_ram_".concat(this.get('slaves_ram_selection')));
		    choice.style.color = "red";
		}
		if (this.get('master_ram_selection') == 0) {
		    var master_ram = this.get('content._data.mem_choices')[0];
		} else {
		    var master_ram = this.get('master_ram_selection');
		}
		if (memories[i] * (this.size_of_cluster() - 1) > (this.get('content._data.mem_av') - master_ram)) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
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
	    var disks = this.get('content._data.disk_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('master_disk_selection') != 0) {
		    var choice = document.getElementById("master_disk_".concat(this.get('master_disk_selection')));
		    choice.style.color = "red";
		}
		if (this.get('slaves_disk_selection') == 0) {
		    var slaves_disk = this.get('content._data.disk_choices')[0];
		} else {
		    var slaves_disk = this.get('slaves_disk_selection');
		}
		if (disks[i] > (this.get('content._data.disk_av') - slaves_disk * (this.size_of_cluster() - 1) )) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
		}
	    }

    	    var elements = document.getElementsByName("slaves_disk_button");
	    var length = elements.length;
	    var disks = this.get('content._data.disk_choices');

	    for (var i = 0; i < length; i++) {
		elements[i].style.color = "initial";
		if (this.get('slaves_disk_selection') != 0) {
		    var choice = document.getElementById("slaves_disk_".concat(this.get('slaves_disk_selection')));
		    choice.style.color = "red";
		}
		if (this.get('master_disk_selection') == 0) {
		    var master_disk = this.get('content._data.disk_choices')[0];
		} else {
		    var master_disk = this.get('master_disk_selection');
		}
		if (disks[i] * (this.size_of_cluster() - 1) > (this.get('content._data.disk_av') - master_disk)) {
		    elements[i].disabled = true;
		} else {
		    elements[i].disabled = false;
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
	size_of_cluster: function(){
	    if ((this.get('cluster_size')=== null) || (this.get('cluster_size')=== undefined)){
	      return 2;
	    }
	    else{
		return this.get('cluster_size');
	    }
	},
	// Reset variables after logout
	reset_variables : function() {
		this.set('master_cpus_Not_Allow', false);
		this.set('slaves_cpus_Not_Allow', false);
		this.set('master_ram_Not_Allow', false);
		this.set('slaves_ram_Not_Allow', false);
		this.set('master_disk_Not_Allow', false);
		this.set('slaves_disk_Not_Allow', false);	
		this.set('storage_Not_Allow', false);
		this.set('cluster_size', 0);
		this.set('master_cpu_selection', 0);
		this.set('slaves_cpu_selection', 0);
		this.set('master_ram_selection', 0);
		this.set('slaves_ram_selection', 0);
		this.set('master_disk_selection', 0);
		this.set('slaves_disk_selection', 0);
		this.set('cluster_name', '');
		this.set('operating_system', 'Debian Base');
		this.set('disk_temp', 'ext_vlmc');
		this.set('message', '');
		this.set('alert_mes_master_cpu', '');
		this.set('alert_mes_master_ram', '');
		this.set('alert_mes_master_disk', '');
		this.set('alert_mes_slaves_cpu', '');
		this.set('alert_mes_slaves_ram', '');
		this.set('alert_mes_slaves_disk', '');
		this.set('alert_mes_cluster_name', '');
	},
	actions : {

		// When a cpu button is clicked, the selected role's cpu selection takes the corresponding value
		cpu_selection : function(value, name) {
		    if (name == "master_cpus_button") {
			if (this.get('slaves_cpu_selection') == 0) {
			    var slaves_cpu = this.get('content._data.cpu_choices')[0];
			} else {
			    var slaves_cpu = this.get('slaves_cpu_selection');
			}
			if (value <= (this.get('content._data.cpu_av') - slaves_cpu * (this.size_of_cluster() - 1) )) {
			    this.set('master_cpu_selection', value);
			}
		    }
		    if (name == "slaves_cpus_button") {
			if (this.get('master_cpu_selection') == 0) {
			    var master_cpu = this.get('content._data.cpu_choices')[0];
			} else {
			    var master_cpu = this.get('master_cpu_selection');
			}		      
			if (value * (this.size_of_cluster() - 1) <= (this.get('content._data.cpu_av') - master_cpu)) {
			    this.set('slaves_cpu_selection', value);
			}
		    }
		},

		// When a memory button is clicked, the selected role's memory selection takes the corresponding value
		ram_selection : function(value, name) {
		    if (this.get('master_ram_selection') == 0) {
			var master_ram = this.get('content._data.mem_choices')[0];
		    } else {
			var master_ram = this.get('master_ram_selection');
		    }
		    if (this.get('slaves_ram_selection') == 0) {
			var slaves_ram = this.get('content._data.mem_choices')[0];
		    } else {
			var slaves_ram = this.get('slaves_ram_selection');
		    }		  
		  		  
		    if (name == "master_ram_button") {
			if (value <= (this.get('content._data.mem_av') - slaves_ram * (this.size_of_cluster() - 1) )) {
			    this.set('master_ram_selection', value);
			}
		    }
		    if (name == "slaves_ram_button") {
			if (value * (this.size_of_cluster() - 1) <= (this.get('content._data.mem_av') - master_ram)) {
			    this.set('slaves_ram_selection', value);
			}
		    }
		},

		// When a disk button is clicked, the selected role's disk selection takes the corresponding value
		disk_selection : function(value, name) {
		  
		    if (this.get('master_disk_selection') == 0) {
			var master_disk = this.get('content._data.disk_choices')[0];
		    } else {
			var master_disk = this.get('master_disk_selection');
		    }
		    if (this.get('slaves_disk_selection') == 0) {
			var slaves_disk = this.get('content._data.disk_choices')[0];
		    } else {
			var slaves_disk = this.get('slaves_disk_selection');
		    }
		  
		    if (name == "master_disk_button") {
			if (value <= (this.get('content._data.disk_av') - slaves_disk * (this.size_of_cluster() - 1) )) {
			    this.set('master_disk_selection', value);
			}
		    }
		    if (name == "slaves_disk_button") {
			if (value * (this.size_of_cluster() - 1) <= (this.get('content._data.disk_av') - master_disk)) {
			    this.set('slaves_disk_selection', value);
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


		// when create cluster button is pressed
		// go_to_create action is triggered
		go_to_create : function() {
		  	this.set('alert_mes_master_cpu', '');
			this.set('alert_mes_master_ram', '');
			this.set('alert_mes_master_disk', '');
			this.set('alert_mes_slaves_cpu', '');
			this.set('alert_mes_slaves_ram', '');
			this.set('alert_mes_slaves_disk', '');
			this.set('alert_mes_cluster_name', '');
			// check that all fields are filled
			if (this.get('master_cpu_selection') == 0) {
				this.set('alert_mes_master_cpu', 'Please select master cpu');
			} else if (this.get('master_ram_selection') == 0) {
				this.set('alert_mes_master_ram', 'Please select master memory');
			} else if (this.get('master_disk_selection') == 0) {
				this.set('alert_mes_master_disk', 'Please select master disk');
			} else if (this.get('slaves_cpu_selection') == 0) {
				this.set('alert_mes_slaves_cpu', 'Please select slaves cpu');  
			} else if (this.get('slaves_ram_selection') == 0) {
				this.set('alert_mes_slaves_ram', 'Please select slaves memory');  
			} else if (this.get('slaves_disk_selection') == 0) {
				this.set('alert_mes_slaves_disk', 'Please select slaves disk');
			} else if (this.get('cluster_name') == '') {
				this.set('alert_mes_cluster_name', 'Please input cluster name'); 
			} else {
				// check if everything is allowed
				if ((this.get('total_cpu_selection') <= this.get("content._data.cpu_av")) && (this.get('total_ram_selection') <= this.get("content._data.mem_av")) && (this.get('total_disk_selection') <= this.get("content._data.disk_av"))) {
					
					var self = this;
					// PUT request
					var cluster_selection = this.store.update('clusterchoice', {
					// set the clusterchoice model with the user choices
					    'id' : 1,
					    'cluster_name' : self.get('cluster_name'),
					    'cluster_size' : self.get('cluster_size'),
					    'cpu_master' : self.get('master_cpu_selection'),
					    'mem_master' : self.get('master_ram_selection'),
					    'disk_master' : self.get('master_disk_selection'),
					    'cpu_slaves' : self.get('slaves_cpu_selection'),
					    'mem_slaves' : self.get('slaves_ram_selection'),
					    'disk_slaves' : self.get('slaves_disk_selection'),
					    'disk_template' : self.get('disk_temp'),
					    'os_choice' : self.get('operating_system')
					}).save();
					cluster_selection.then(function(data) {
					    // Set the response to user's create cluster click when put succeeds.
					    self.set('message', data._data.message);
					}, function() {
					    // Set the response to user's create cluster click when put fails.
					    self.set('message', 'A problem occured during your request. Please check your cluster parameters and try again');
					});
					
				} else {
					alert('Requested resources unavailable!');
				}
			}
		},
	}
});
