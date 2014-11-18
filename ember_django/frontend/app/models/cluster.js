attr = App.attr;
// Model used for retrieving cluster creation information based on user's quota and kamaki flavors
App.Cluster = DS.Model.extend({
	vms_max : attr('number'),    // maximum (limit) number of VMs
	vms_av : attr(),             // available VMs
	cpu_max : attr('number'),    // maximum CPUs
	cpu_av : attr('number'),     // available CPUs
	mem_max : attr('number'),    // maximum memory
	mem_av : attr('number'),     // available memory
	disk_max : attr('number'),   // maximum disk space
	disk_av : attr('number'),    // available disk space
	cpu_choices : attr(),        // CPU choicses
	mem_choices : attr(),        // memory choices
	disk_choices : attr(),       // disk choices
	disk_template : attr(),      // storage choices
	os_choices : attr()          // Operating System choices
});
