// Createcluster index controller
App.CreateclusterIndexController = Ember.Controller.extend({
	master_enabled : false,
	slaves_enabled : false,
	cpu_Not_Allow : true,
	mem_Not_Allow : true,
	disk_Not_Allow : true,
	storage_Not_Allow : true,
	cluster_size : 2,
	master_color : 'lightblue',
	slaves_color : 'lightblue',

	// If cluster size is less than two disable slaves option
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

	cluster_name : '',
	operating_system : 'Debian Base',

	master_cpu_selection : 0,
	slaves_cpu_selection : 0,

	total_cpu_selection : function() {
		return (this.get('master_cpu_selection') + this.get('slaves_cpu_selection') * (this.get('cluster_size') - 1));
	}.property('master_cpu_selection', 'slaves_cpu_selection', 'cluster_size'),

	cpu_available : function() {
		var cpu_avail = this.get('content._data.cpu_av') - this.get('total_cpu_selection');
		if (cpu_avail < 0) {
			alert('The cluster size you selected with the current cpu choices exceed the cpu quota. You should lower the clustersize, change cpu values and select the clustersize again');
		} else {
			return cpu_avail;
		}
	}.property('total_cpu_selection'),

	master_mem_selection : 0,
	slaves_mem_selection : 0,

	total_mem_selection : function() {
		return (this.get('master_mem_selection') + this.get('slaves_mem_selection') * (this.get('cluster_size') - 1));
	}.property('master_mem_selection', 'slaves_mem_selection', 'cluster_size'),

	mem_available : function() {
		mem_avail = this.get('content._data.mem_av') - this.get('total_mem_selection');
		if (mem_avail < 0) {
			alert('The cluster size you selected with the current ram choices exceed the ram quota. You should lower the clustersize, change ram values and select the clustersize again');
		} else {
			return mem_avail;
		}
	}.property('total_mem_selection'),

	master_disk_selection : 0,
	slaves_disk_selection : 0,

	total_disk_selection : function() {
		return (this.get('master_disk_selection') + this.get('slaves_disk_selection') * (this.get('cluster_size') - 1));
	}.property('master_disk_selection', 'slaves_disk_selection', 'cluster_size'),

	disk_available : function() {
		disk_avail = this.get('content._data.disk_av') - this.get('total_disk_selection');
		if (disk_avail < 0) {
			alert('The cluster size you selected with the current disk choices exceed the disk quota. You should lower the clustersize, change disk values and select the clustersize again');
		} else {
			return disk_avail;
		}
	}.property('total_disk_selection'),

	// Computes the maximum vms that can be build with current flavor choices and return this to drop down menu on index
	max_cluster_size_av : function() {
		var length = this.get('content._data.vms_av').length;
		var max_cluster_size_limited_by_current_cpus = [];
		var max_cluster_size_limited_by_current_mems = [];
		var max_cluster_size_limited_by_current_disks = [];
		this.buttons();
		//  alert(max_cluster_size_limited_by_current_cpus);
		//   alert('max_cluster_size_limited_by_current_cpus');
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

	// Functionality about cpu buttons coloring and enable-disable responding to user events
	cpu_buttons : function() {
		var elements = document.getElementsByName("cpu_button");
		var length = elements.length;
		var cpus = this.get('content._data.cpu_choices');
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_cpu_selection') != 0) {
					var choice = document.getElementById(this.get('master_cpu_selection'))
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
					var choice = document.getElementById(this.get('slaves_cpu_selection'))
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

	// Functionality about memory buttons coloring and enable-disable responding to user events
	memory_buttons : function() {
		var elements = document.getElementsByName("mem_button");
		var length = elements.length;
		var memories = this.get('content._data.mem_choices');
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_mem_selection') != 0) {
					var choice = document.getElementById(this.get('master_mem_selection'))
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
					var choice = document.getElementById(this.get('slaves_mem_selection'))
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

	// Functionality about disk buttons coloring and enable-disable responding to user events
	disk_buttons : function() {
		var elements = document.getElementsByName("disk_button");
		var length = elements.length;
		var disks = this.get('content._data.disk_choices');
		var last = disks.length;
		if (this.master_enabled) {
			for (var i = 0; i < length; i++) {
				elements[i].style.color = "initial";
				if (this.get('master_disk_selection') != 0) {
					var choice = document.getElementById(this.get('master_disk_selection'))
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
					var choice = document.getElementById(this.get('slaves_disk_selection'))
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

	// Functionality about storage buttons coloring upon selection responding to user events
	storage_buttons : function() {
		var elements = document.getElementsByName("storage_button");
		var length = elements.length;
		var disks = this.get('content._data.disk_template');
		for (var i = 0; i < length; i++) {
			elements[i].style.color = "initial";
			var choice = document.getElementById(this.get('disk_temp'))
			choice.style.color = "red";
		}
	},

	buttons : function() {
		this.cpu_buttons();
		this.memory_buttons();
		this.disk_buttons();
		this.storage_buttons();
	},

	disk_temp : 'ext_vlmc',
	actions : {

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

		disk_template : function(name) {
			this.set('disk_temp', name);
			this.storage_buttons();
		},

		logout : function() {
			// redirect to logout
			this.transitionTo('user.logout');
		},

		display_master : function() {

			this.set('master_color', 'lightgreen');
			this.set('slaves_color', 'lightgrey');
			this.set('master_enabled', true);
			this.set('slaves_enabled', false);
			this.buttons();
			this.set('storage_Not_Allow', false);
		},

		display_slaves : function() {

			this.set('master_color', 'lightgrey');
			this.set('slaves_color', 'lightgreen');
			this.set('master_enabled', false);
			this.set('slaves_enabled', true);
			this.buttons();
			this.set('storage_Not_Allow', false);
		},

		// when next button is pressed
		// gotoconfirm action is triggered
		gotoconfirm : function() {

			// check all fields are filled
			if (this.get('master_cpu_selection') == 0) {
				alert('Please select master cpu');
			} else if ((this.get('slaves_cpu_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves cpu');
			} else if (this.get('master_mem_selection') == 0) {
				alert('Please select master memory');
			} else if ((this.get('slaves_mem_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves memory');
			} else if (this.get('master_disk_selection') == 0) {
				alert('Please select master disk');
			} else if ((this.get('slaves_disk_selection') == 0) && !this.get('slaves_Not_Allow')) {
				alert('Please select slaves disk');
			} else if (this.get('cluster_name') == '') {
				alert('Please select cluster name');
			} else if (this.disk_temp == '') {
				alert('Please select storage');
			} else {
				// check if everything is allowed
				if ((this.get('total_cpu_selection') <= this.get("content._data.cpu_av")) && (this.get('total_mem_selection') <= this.get("content._data.mem_av")) && (this.get('total_disk_selection') <= this.get("content._data.disk_av"))) {
					// redirect to confirm template
					this.transitionTo('createcluster.confirm');
				} else {
					alert('Requested resources unavailable!');
				}
			}
		},
	},
	master_style : function() {
		return "background-color:" + this.get('master_color');
	}.property('master_color'),
	slaves_style : function() {
		return "background-color:" + this.get('slaves_color');
	}.property('slaves_color')
});
