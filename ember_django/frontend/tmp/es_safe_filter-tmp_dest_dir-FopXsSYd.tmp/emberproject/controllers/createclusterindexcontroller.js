// Createcluster index controller
Orka.CreateclusterIndexController = Ember.Controller.extend({
        master_enabled : true,
        slaves_enabled : false,
        cpu_Not_Allow : false,
        mem_Not_Allow : false,
        disk_Not_Allow : false,
        cluster_size : 2,
        slaves_Not_Allow : function() {
                if (this.get('cluster_size') < 2) {
                        return true;
                } else {
                        return false;
                }
        }.property('cluster_size'),
        cluster_name : '',
        operating_system : 'Debian Base',
        master_color : 'lightgreen',
        slaves_color : 'lightgrey',

        master_cpu_selection : 0,
        slaves_cpu_selection : 0,

        total_cpu_selection : function() {
                return this.get('master_cpu_selection') + this.get('slaves_cpu_selection') * (this.get('cluster_size') - 1);
        }.property('master_cpu_selection', 'slaves_cpu_selection', 'cluster_size'),

        cpu_available : function() {
                var cpu_avail = this.get('content._data.cpu_av') - this.get('total_cpu_selection');
                if (cpu_avail < 0) {
                        this.set('cpu_Not_Allow', true);
                        alert('The cluster size you selected with the current cpu choices exceed the cpu quota. You should lower the clustersize, change cpu values and select the clustersize again');

                } else {
                        this.set('cpu_Not_Allow', false);
                        return cpu_avail;
                }
        }.property('total_cpu_selection'),

        master_mem_selection : 0,
        slaves_mem_selection : 0,

        total_mem_selection : function() {
                return this.get('master_mem_selection') + this.get('slaves_mem_selection') * (this.get('cluster_size') - 1);
        }.property('master_mem_selection', 'slaves_mem_selection', 'cluster_size'),

        mem_available : function() {
                mem_avail = this.get('content._data.mem_av') - this.get('total_mem_selection');
                if (mem_avail < 0) {
                        this.set('mem_Not_Allow', true);
                        alert('The cluster size you selected with the current ram choices exceed the ram quota. You should lower the clustersize, change ram values and select the clustersize again');
                } else {
                        this.set('mem_Not_Allow', false);
                        return mem_avail;
                }
        }.property('total_mem_selection'),

        master_disk_selection : 0,
        slaves_disk_selection : 0,

        total_disk_selection : function() {
                return this.get('master_disk_selection') + this.get('slaves_disk_selection') * (this.get('cluster_size') - 1);
        }.property('master_disk_selection', 'slaves_disk_selection', 'cluster_size'),

        disk_available : function() {
                disk_avail = this.get('content._data.disk_av') - this.get('total_disk_selection');
                if (disk_avail < 0) {
                        this.set('disk_Not_Allow', true);
                        alert('The cluster size you selected with the current disk choices exceed the disk quota. You should lower the clustersize, change disk values and select the clustersize again');
                } else {
                        this.set('disk_Not_Allow', false);
                        return disk_avail;
                }
        }.property('total_disk_selection'),

        disk_temp : 'ext_vlmc',
        actions : {

                cpu_selection : function(name) {
                        if (this.master_enabled) {
                                if (name > (this.get('content._data.cpu_av') - this.get('slaves_cpu_selection') * (this.get('cluster_size') - 1) )) {
                                        alert('This cpu choice exceed your quota. Please select a lower cpu value');
                                } else {
                                        this.set('master_cpu_selection', name);
                                }
                        }
                        if (this.slaves_enabled) {
                                if (name * (this.get('cluster_size') - 1) > (this.get('content._data.cpu_av') - this.get('master_cpu_selection'))) {
                                        alert('This cpu choice exceed your quota. Please select a lower cpu value');
                                } else {
                                        this.set('slaves_cpu_selection', name);
                                }
                        }
                },
                mem_selection : function(name) {
                        if (this.master_enabled) {
                                if (name > (this.get('content._data.mem_av') - this.get('slaves_mem_selection') * (this.get('cluster_size') - 1) )) {
                                        alert('This ram choice exceed your quota. Please select a lower ram value');
                                } else {
                                        this.set('master_mem_selection', name);
                                }
                        }
                        if (this.slaves_enabled) {
                                if (name * (this.get('cluster_size') - 1) > (this.get('content._data.mem_av') - this.get('master_mem_selection'))) {
                                        alert('This ram choice exceed your quota. Please select a lower ram value');
                                } else {
                                        this.set('slaves_mem_selection', name);
                                }
                        }
                },
                disk_selection : function(name) {
                        if (this.master_enabled) {
                                if (name > (this.get('content._data.disk_av') - this.get('slaves_disk_selection') * (this.get('cluster_size') - 1) )) {
                                        alert('This disk choice exceed your quota. Please select a lower disk size value');
                                } else {
                                        this.set('master_disk_selection', name);
                                }
                        }
                        if (this.slaves_enabled) {
                                if (name * (this.get('cluster_size') - 1) > (this.get('content._data.disk_av') - this.get('master_disk_selection'))) {
                                        alert('This disk choice exceed your quota. Please select a lower disk size value');
                                } else {
                                        this.set('slaves_disk_selection', name);
                                }
                        }
                },

                disk_template : function(name) {

                        this.set('disk_temp', name);
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
                },
                display_slaves : function() {

                        this.set('master_color', 'lightgrey');
                        this.set('slaves_color', 'lightgreen');
                        this.set('master_enabled', false);
                        this.set('slaves_enabled', true);
                },
                // when next button is pressed
                // gotoconfirm action is triggered
                gotoconfirm : function() {

                        // check all fields are filled
                        if ((this.master_cpu_selection == '') || (this.slaves_cpu_selection == '') || (this.master_mem_selection == '') || (this.slaves_mem_selection == '') || (this.master_disk_selection == '') || (this.slaves_disk_selection == '') || (this.disk_temp == '') || (this.get('cluster_name') == '')) {
                                alert('Something is missing!');
                        } else {
                                // check if everything is allowed

                                if ((this.get('total_cpu_selection') <= this.get("content._data.cpu_av")) && (this.get('total_mem_selection') <= this.get("content._data.mem_av")) && (this.get('total_disk_selection') <= this.get("content._data.disk_av"))) {
                                        // redirect to confirm template
                                        this.transitionTo('createcluster.confirm');
                                } else {
                                        alert('Requested resources unavailable!');
                                }
                        }
                }
        },
        master_style : function() {
                return "background-color:" + this.get('master_color');
        }.property('master_color').cacheable(),
        slaves_style : function() {
                return "background-color:" + this.get('slaves_color');
        }.property('slaves_color').cacheable()
});
