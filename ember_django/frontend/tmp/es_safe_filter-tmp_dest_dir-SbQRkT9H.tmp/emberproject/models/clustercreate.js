// Model used for retrieving create cluster information based on user's quota and kamaki flavors
Orka.Createcluster = DS.Model.extend({
	vms_max : DS.attr('number'),    // maximum (limit) number of VMs
	vms_av : DS.attr(),             // available VMs
	cpu_max : DS.attr('number'),    // maximum CPUs
	cpu_av : DS.attr('number'),     // available CPUs
	mem_max : DS.attr('number'),    // maximum memory
	mem_av : DS.attr('number'),     // available memory
	disk_max : DS.attr('number'),   // maximum disk space
	disk_av : DS.attr('number'),    // available disk space
	cpu_choices : DS.attr(),        // CPU choicses
	mem_choices : DS.attr(),        // memory choices
	disk_choices : DS.attr(),       // disk choices
	disk_template : DS.attr(),      // storage choices
	os_choices : DS.attr()          // Operating System choices
});
