attr = App.attr;
// Model used for retrieving cluster creation information 
// based on user's quota and kamaki flavors
App.Cluster = DS.Model.extend({
	project_name : attr(),		    // name of the project
	vms_max : attr('number'),    	// maximum (limit) number of VMs
	vms_av : attr(),             	// available VMs
	cpu_max : attr('number'),    	// maximum CPUs
	cpu_av : attr('number'),     	// available CPUs
	mem_max : attr('number'),    	// maximum memory
	mem_av : attr('number'),     	// available memory
	disk_max : attr('number'),  	// maximum disk space
	disk_av : attr('number'),    	// available disk space
	net_av : attr(),                // available networks
	floatip_av : attr(),            // available floating ips	
	cpu_choices : attr(),        	// CPU choicses
	mem_choices : attr(),        	// memory choices
	disk_choices : attr(),       	// disk choices
	disk_template : attr(),      	// storage choices
	os_choices : attr(),          	// Operating System choices
	vm_flavors_choices : ['Small', 'Medium', 'Large'],  //Predefined VM Flavors
	ssh_keys_names : attr()         // ssh key's names
});

// For Fixtures
/*App.Cluster.reopenClass({
FIXTURES: [
    {
	id: 1,
	project_name : 'system',
	vms_max : 16,
	vms_av : [2,4,8,16],
	cpu_max : 32,
	cpu_av : 32,
	mem_max : 2048,
	mem_av : 2048,
	disk_max : 200,
	disk_av : 100,
	cpu_choices : [1,2,4,8],
	mem_choices : [128, 256,512],
	disk_choices : [20,40,60,80,100],
	disk_template : ['disk1','disk2'],
	os_choices : ['os1','os2']
    },
    {
	id: 2,
	project_name : 'escience.grnet.gr',
	vms_max : 32,
	vms_av : [8,16],
	cpu_max : 32,
	cpu_av : 16,
	mem_max : 2048,
	mem_av : 1024,
	disk_max : 400,
	disk_av : 200,
	cpu_choices : [4,8],
	mem_choices : [256,512],
	disk_choices : [50,100],
	disk_template : ['disk3','disk4'],
	os_choices : ['os3','os4']
    }
]
});*/
