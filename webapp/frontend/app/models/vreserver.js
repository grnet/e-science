attr = App.attr;
safestr = Ember.Handlebars.SafeString;
// Model used for retrieving VRE server creation information 
// based on user's quota and kamaki flavors
App.Vreserver = DS.Model.extend({
	project_name : attr(),		    // name of the project
	vms_max : attr('number'),    	// maximum (limit) number of VMs
	vms_av : attr(),             	// available VMs
	cpu_max : attr('number'),    	// maximum CPUs
	cpu_av : attr('number'),     	// available CPUs
	ram_max : attr('number'),    	// maximum ram
	ram_av : attr('number'),     	// available ram
	disk_max : attr('number'),  	// maximum disk space
	disk_av : attr('number'),    	// available disk space
	floatip_av : attr(),            // available floating ips	
	cpu_choices : attr(),        	// CPU choices
	ram_choices : attr(),        	// ram choices
	disk_choices : attr(),       	// disk choices
	disk_template : attr(),      	// storage choices
	os_choices : attr(),          	// Operating System choices
	vre_choices : function(){
	    return this.get('os_choices')[1];
	}.property('os_choices','project_name'),       // Filter for VRE images
	project_name_clean : function(){
	    var project_name = this.get('project_name');
	    var numchar = project_name.lastIndexOf(":");
	    return numchar == -1 ? project_name : project_name.slice(0,numchar);
	}.property('project_name'),     // Remove guid from system project name
	project_name_decorated : function(){
	    var name = this.get('project_name_clean');
	    var template_bs3 = '<span class="col col-sm-3 text-left pull-left">%@ </span>'+
    	                   '<span class="col col-sm-2 text-right pull-left">VM:%@</span>'+
    	                   '<span class="col col-sm-2 text-right pull-left">CPU:%@</span>'+
    	                   '<span class="col col-sm-3 text-right pull-left">RAM:%@MB</span>'+
    	                   '<span class="col col-sm-2 text-right pull-left">Disk:%@GB</span>';
	    var decorated_name = template_bs3.fmt(name,this.get('vms_max'),this.get('cpu_av'),this.get('ram_av'),this.get('disk_av'));
        return new safestr(decorated_name);
	}.property('project_name_clean'), // decorate project name with project resource info in columns
	ssh_keys_names : attr()         // ssh key's names
});

