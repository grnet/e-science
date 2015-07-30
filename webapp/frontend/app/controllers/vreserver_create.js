// VRE Server Create controller
App.VreserverCreateController = Ember.Controller.extend({
	needs : ['userWelcome', 'vreserverManagement'],
	// populated with VRE image component info from controllers.application
	vreImages : [],
	/*
	 * Static Data
	 */
	// client-side only, eventually add data structure to the backend
	vreCategoryLabels : ['Portal/Cms','Wiki','Project Management'],
	vreCategoryData : {
	    'Portal/Cms' : ['Deb8-Drupal-Docker'],
	    'Wiki' : ['Deb8-Mediawiki-Docker'],
	    'Project Management': ['Deb8-Redmine-Docker'] 
	},
	// client-side only
	vreFlavorLabels : ['Small', 'Medium', 'Large'],
	vreFlavorData : [
	   {cpu:1,ram:1024,disk:5}, //Small
	   {cpu:2,ram:2048,disk:10},//Medium
	   {cpu:4,ram:4096,disk:20} //Large
	],
	/*
	 * Project selection:
	 */
	// anything not available without project 
	// should observe this or a chained observer
	boolean_no_project : function(){
	    return Ember.isEmpty(this.get('selected_project_id'));
	}.property('selected_project_id'),
	selected_project_description : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('project_name_clean') : '';
	}.property('boolean_no_project'),
	selected_project_name : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('project_name') : '';
	}.property('selected_project_id'),
	// vm  
    selected_project_available_vm : function(){
        return !this.get('boolean_no_project') ? Number(this.get('content').objectAt(this.get('selected_project_id')-1).get('vms_max')) : 0;
    }.property('selected_project_id'),
    // floating ip
    selected_project_available_ip : function(){
        return !this.get('boolean_no_project') ? Number(this.get('content').objectAt(this.get('selected_project_id')-1).get('floatip_av')) : 0;
    }.property('selected_project_id'),
    /*
     * VRE Categories
     */
    // wrap categories to a project selection check
    vre_categories : function(){
        return !this.get('boolean_no_project') ? this.get('vreCategoryLabels') : [];
    }.property('selected_project_id'),
    selected_category_static : null,
    selected_category : function(key,value){
        if (arguments.length>1){// setter
            this.set('selected_category_id_static',value);
        }
        return this.get('selected_category_id_static'); // getter
    }.property('selected_category_id_static','selected_project_id'),
    /*
     * VRE Images
     */
	selected_project_images : function(){
	    //TODO:  model data, not used at moment until we implement dynamic filtering on image category
	    var arr_images = !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('vre_choices') : [];
	    // return based on static data defined at top of controller, after verification with model data
	    var arr_filtered_by_category = !Ember.isEmpty(this.get('selected_category')) ? this.get('vreCategoryData')[this.get('selected_category')] : [];
	    var arr_verified = arr_filtered_by_category.filter(function(item,index,self){// remove any statics not on model
	        return arr_images.contains(item) ? true : false;
	    });
	    return !this.get('boolean_no_project') ? arr_verified : [];
	}.property('vre_categories.[]','selected_category'),
	selected_image_static : null,
	selected_image : function(key,value){
        if (arguments.length>1){// setter
            this.set('selected_image_static',value);
        }
        return this.get('selected_image_static');// getter
    }.property('selected_image_static', 'selected_project_id'),
    /*
     * SSH Keys
     */
	selected_project_sshkeys : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('ssh_keys_names') : [];
	}.property('boolean_no_project'),
	selected_sshkey_static : null,
	selected_sshkey : function(key,value){
	    if (arguments.length>1){// setter
            this.set('selected_sshkey_static',value);
        }
        return Ember.isEmpty(this.get('selected_sshkey_static')) ? 'no_ssh_key_selected' : this.get('selected_sshkey_static');// getter
	}.property('selected_sshkey_static', 'selected_project_id'),
	/*
	 * Storage
	 */
	selected_project_storage_choices : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_template') : [];
	}.property('boolean_no_project'),
	selected_storage_description : function(){
	    return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_storage_id')) ? 
        this.get('selected_project_storage_choices')[this.get('selected_storage_id')] : '';
	}.property('selected_storage_id','selected_project_id'),
    /*
     * Flavors
     */
    // wrap flavor choices to a project selection check
    vre_flavor_choices : function(){
        return !this.get('boolean_no_project') ? this.get('vreFlavorLabels') : [];
    }.property('boolean_no_project'),
    selected_vre_flavor_data : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_flavor_id')) ? this.get('vreFlavorData')[this.get('selected_flavor_id')] : [];
    }.property('selected_flavor_id','selected_project_id'),	
	/*
	 * VRE Hardware settings
	 */
	// cpu
    selected_project_available_cpu : function(){
        var selected_cpu_value = Ember.isEmpty(this.get('selected_cpu_value')) ? 0 : Number(this.get('selected_cpu_value'));
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('cpu_av')-selected_cpu_value : 0;
    }.property('selected_cpu_value','selected_project_id'),
    selected_project_cpu_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('cpu_choices') : [];
    }.property('selected_project_id'),
    selected_cpu_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_cpu_id')) ? 
        this.get('selected_project_cpu_choices')[this.get('selected_cpu_id')] : 
        this.set('selected_cpu_id',null) && '';
    }.property('selected_cpu_id','selected_project_id'),
    // ram
    selected_project_available_ram : function(){
        var selected_ram_value = Ember.isEmpty(this.get('selected_ram_value')) ? 0 : Number(this.get('selected_ram_value'));
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('ram_av')-selected_ram_value : 0;
    }.property('selected_ram_value','selected_project_id'),
    selected_project_ram_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('ram_choices') : [];
    }.property('selected_project_id'),
    selected_ram_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_ram_id')) ? 
        this.get('selected_project_ram_choices')[this.get('selected_ram_id')] : 
        this.set('selected_ram_id',null) && '';
    }.property('selected_ram_id','selected_project_id'),
    // disk 
    selected_project_available_disk : function(){
        var selected_disk_value = Ember.isEmpty(this.get('selected_disk_value')) ? 0 : Number(this.get('selected_disk_value'));
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_av')-selected_disk_value : 0;
    }.property('selected_disk_value','selected_project_id'),
    selected_project_disk_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_choices') : [];
    }.property('selected_project_id'),
    selected_disk_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_disk_id')) ? 
        this.get('selected_project_disk_choices')[this.get('selected_disk_id')] : 
        this.set('selected_disk_id',null) && '';
    }.property('selected_disk_id','selected_project_id'),    
    /*
     * Actions
     */
    actions : {
        focus_project_selection : function(){
            $('#id_project_id').fadeTo(700,0.4).focus().fadeTo(300,1.0);
        },
        pick_storage : function(index, value){
            this.set('selected_storage_id',index);
            $('#id_storage_choice > label').removeClass("active btn-success");
            var selector = '#id_storage_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
        },
        pick_flavor : function(index, value){
            this.set('selected_flavor_id',index);
            $('#id_vre_flavors > label').removeClass("active btn-success");
            var selector = '#id_vre_flavors #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            this.send('pick_cpu',index,this.get('selected_project_cpu_choices')[index]);
            this.send('pick_ram',index,this.get('selected_project_ram_choices')[index]);
            this.send('pick_disk',index,this.get('selected_project_disk_choices')[index]);
        },
        pick_cpu : function(index, value){
            this.set('selected_cpu_id',index);
            $('#id_cpu_choice > label').removeClass("active btn-success");
            var selector = '#id_cpu_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
        },
        pick_ram : function(index, value){
            this.set('selected_ram_id',index);
            $('#id_ram_choice > label').removeClass("active btn-success");
            var selector = '#id_ram_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
        },
        pick_disk : function(index, value){
            this.set('selected_disk_id',index);
            $('#id_disk_choice > label').removeClass("active btn-success");
            var selector = '#id_disk_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
        },
        apply_last_config : function(){
            console.log('clicked apply last');
        },
        submit_create : function(){
            console.log('clicked create');
            var that = this;
            var new_server = {
                'project_name': that.get('selected_project_name'), 
                'server_name': that.get('vre_server_name'),
                'cpu': that.get('selected_cpu_value'), 
                'ram': that.get('selected_ram_value'),
                'disk': that.get('selected_disk_value'), 
                'disk_template': that.get('selected_storage_description'),
                'os_image': that.get('selected_image'),
                'ssh_key_selection': that.get('selected_sshkey')
            };
            this.store.fetch('user',1).then(function(user){
                //success
                console.log(new_server);
                var new_record = that.store.createRecord('uservreserver',new_server);
                new_record.save().then(function(data){
                    that.set('controllers.userWelcome.create_cluster_start', true);
                    that.get('controllers.userWelcome').send('setActiveTab','vreservers');
                    that.transitionToRoute('user.welcome');
                },function(reason){
                    console.log(reason);
                });
            },function(reason){
                //error
                console.log(reason);
            });
        },
        cancel : function(){
            this.set('selected_project_id',null);
            this.set('vre_server_name',null);
            this.transitionToRoute('user.welcome');
        }
    }
});
