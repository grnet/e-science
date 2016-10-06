// VRE Server Create controller
App.VreserverCreateController = Ember.Controller.extend({
	needs : ['application', 'userWelcome', 'vreserverManagement'],
	// populated with VRE image component info from controllers.application
	vreImages : [],
	/*
	 * Static Data
	 */
	// mapping of uservreserver model properties to controller computed properties
	model_to_controller_map : {
        project_name: 'selected_project_name', 
        server_name: 'vre_server_name',
        cpu: 'selected_cpu_value', 
        ram: 'selected_ram_value',
        disk: 'selected_disk_value', 
        disk_template: 'selected_storage_description',
        os_image: 'selected_image',
        ssh_key_selection: 'selected_sshkey',
        admin_password: 'vre_admin_pass',
        admin_email: 'vre_admin_email'
	},
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
	}.property('selected_project_id'),
	selected_project_name : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('project_name') : '';
	}.property('selected_project_id'),
	// vm  get the last item of the array of available VMs
    selected_project_available_vm : function(){
        return !this.get('boolean_no_project') ? Number(this.get('content').objectAt(this.get('selected_project_id')-1).get('vms_av').get("lastObject")) || 0 : 0;
    }.property('selected_project_id'),
    // floating ip
    selected_project_available_ip : function(){
        return !this.get('boolean_no_project') ? Number(this.get('content').objectAt(this.get('selected_project_id')-1).get('floatip_av')) : 0;
    }.property('selected_project_id'),
    selected_project_changed : function(){
        this.send('clear_cached');
    }.observes('selected_project_id'),
    /*
     * VRE Categories
     */
    vreCategoryLabels : function(){
        var arrLabels = [];
        var vreImages = this.get('vreImages');
        for (i=0;i<vreImages.length;i++){
            arrLabels.push(vreImages[i].get('image_category'));
        }
        return arrLabels.uniq();
    }.property(),
    // wrap categories to a project selection check
    vre_categories : function(){
        return !this.get('boolean_no_project') ? this.get('vreCategoryLabels') : [];
    }.property('selected_project_id'),
    selected_category_static : null, // need this one-way bound property to workaround ember #select bug
    selected_category : function(key,value){
        if (arguments.length>1){// setter
            this.set('selected_category_static',value);
            this.set('selected_image',null);
        }
        return this.get('selected_category_static'); // getter
    }.property('selected_category_static','selected_project_id'),
    /*
     * VRE Images
     */
    vreImageExtraProperties_static : {},
    vreImageExtraProperties : function(that){
        // follow a naming convention when referencing in templates
        // "show_<extra_field_name>_input" (eg. show_admin_password_input)
        // data structure {'controller_field_boolean': ['image_name1','image_name2',...]}
        var self = that; // get the controller into self
        var vreImages = self.get('vreImages');
        var extra_properties = self.get('vreImageExtraProperties_static');
        for (i=0;i<vreImages.length;i++){
            var imageName = vreImages[i].get('image_name');
            var arrImageFields = vreImages[i].get('image_init_extra');
            for (j=0;j<arrImageFields.length;j++) {
                var propName = 'show_%@_input'.fmt(arrImageFields[j]);
                Ember.isEmpty(extra_properties[propName]) ? extra_properties[propName] = [] : $.noop();
                !(extra_properties[propName]).contains(imageName) && (extra_properties[propName]).push(imageName);
            }
        }
        return extra_properties;
    },    
    vreImageExtraFields : function(){
        // data structure {'image_name': ['field1','field2',...]}
        var objExtraFields = {};
        var vreImages = this.get('vreImages');
        for (i=0;i<vreImages.length;i++){
            objExtraFields[vreImages[i].get('image_name')]=vreImages[i].get('image_init_extra');
        }
        return objExtraFields;
    }.property(),    
    vreResourceMin : function(){
        var objRequirements = {};
        var vreImages = this.get('vreImages');
        for (i=0;i<vreImages.length;i++){
            objRequirements[vreImages[i].get('image_name')]=vreImages[i].get('image_min_reqs');
        }
        return objRequirements;
    }.property(),    
	selected_project_images : function(){
	    var arr_project_images = !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('vre_choices') : [];
	    var selected_category = this.get('selected_category') || '';
	    var arr_images = this.get('vreImages');
	    var arr_available_images = [];
	    for (i=0;i<arr_images.get('length');i++){//filter by selected category and verify image is available on selected project
	        if ((arr_images[i].get('image_category')==selected_category) 
	        && (arr_project_images.contains(arr_images[i].get('image_name')))){
	            arr_available_images.push(arr_images[i].get('image_name'));
	        }
	    }
	    return !this.get('boolean_no_project') ? arr_available_images : [];
	}.property('vre_categories.[]','selected_category'),
	selected_image_static : null,
	selected_image : function(key,value){
        if (arguments.length>1){// setter
            this.set('selected_image_static',value);
        }
        return this.get('selected_image_static');// getter
    }.property('selected_image_static', 'selected_project_id'),
    selected_image_popover : false,
    selected_image_components : function(){
        // decorate with image component info
        var html_templ = '%@%@: <span class="text text-info pull-right">%@</span><br>';
        var html_snippet = '<h5 class="strong">Component: <span class="text text-info">Version</span></h5>';
        var image_data = this.get('vreImages');
        var extra_fields = this.get('vreImageExtraProperties')(this);
        for (property in extra_fields){
            this.set(property,null);
        }
        for (i=0; i<image_data.length; i++){
            if (image_data[i].get('image_name') == this.get('selected_image')){
                var arr_image_components = image_data[i].get('image_components');
                for (j=0; j<arr_image_components.length; j++){
                    html_snippet = html_templ.fmt(html_snippet, arr_image_components[j]['name'], arr_image_components[j]['property']['version']);
                }
                for (property in extra_fields){
                    if (extra_fields[property].contains(this.get('selected_image')) || extra_fields[property].contains('*')){
                        this.set(property,true);
                    }
                }
                this.set('selected_image_popover',true);
                return html_snippet;
            }
        }
        this.set('selected_image_popover',null);
        this.set('vre_admin_pass',null);
        return '';
    }.property('selected_image','selected_category'),
    selected_image_changed : function(){
        if (!Ember.isEmpty(this.get('selected_image'))) this.set('alert_missing_input_image',null);
    }.observes('selected_image'),
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
    reverse_storage_lookup : function(){
        var storage_lookup = this.get('AppSettings').filterBy('section','Cyclades').filterBy('property_name','Storage');
        return JSON.parse(storage_lookup[0].get('property_value'));
    }.property(),	
	selected_project_storage_choices : function(){
	    return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_template') : [];
	}.property('boolean_no_project'),
	selected_storage_description : function(){
	    return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_storage_id')) ? 
        this.get('selected_project_storage_choices')[this.get('selected_storage_id')] : '';
	}.property('selected_storage_id','selected_project_id'),
	selected_storage_auto : function(){
        var that = this;
        Ember.run.later(function() {
            if (that.get('selected_project_storage_choices').length == 1) {
                that.send('pick_storage', 0, that.get('selected_project_storage_choices')[0]);
            } else if (that.get('boolean_no_project')) {
                that.set('selected_project_description', '');
            }
        }, 300);
	}.observes('selected_project_storage_choices.[]'),
    /*
     * Flavors
     */
    vreFlavorLabels : function(){
        var vreFlavors = this.get('AppSettings').filterBy('section','VRE_Flavor').sortBy('id');
        var arrFlavorLabels = [];
        for (i=0;i<vreFlavors.length;i++){
            arrFlavorLabels.push(vreFlavors[i].get('property_name'));
        }
        return arrFlavorLabels;
    }.property(),
    vreFlavorData : function(){
        var vreFlavors = this.get('AppSettings').filterBy('section','VRE_Flavor').sortBy('id');
        var arrFlavorData = [];
        for (i=0;i<vreFlavors.length;i++){
            arrFlavorData.push(JSON.parse(vreFlavors[i].get('property_value')));
        }
        return arrFlavorData;
    }.property(),    
    // wrap flavor choices to a project selection check
    vre_flavor_choices : function(){
        return this.get('vreFlavorLabels');
    }.property('boolean_no_project'),
    vre_flavor_available_choices : function(){
        var flavor_choices = this.get('vre_flavor_choices');
        var flavor_data = this.get('vreFlavorData');
        var flavor_choices_available = flavor_data.map(function(item,index){
            var cpu_valid = item.cpu <= this.get('selected_project_available_cpu');
            var ram_valid = item.ram <= this.get('selected_project_available_ram');
            var disk_valid = item.disk <= this.get('selected_project_available_disk');
            return (cpu_valid && ram_valid && disk_valid) && {value:flavor_choices[index], disabled:false} || {value:flavor_choices[index], disabled:true}; 
        },this);
        return !this.get('boolean_no_project') ? flavor_choices_available : [];
    }.property('vre_flavor_choices.[]'),
    selected_vre_flavor_changed : function(){
        if (Ember.isEmpty(this.get('selected_flavor_id'))){
            Ember.run.later(function(){
                $('#id_vre_flavors > label').length > 0 && $('#id_vre_flavors > label').removeClass("active btn-success");
            },300);
        }
    }.observes('selected_flavor_id'),
	/*
	 * VRE Hardware settings
	 */
	// CPU
    selected_project_available_cpu : function(){
        var selected_cpu_value = Ember.isEmpty(this.get('selected_cpu_value')) ? 0 : Number(this.get('selected_cpu_value'));
        this.set('alert_no_project_resources',null);
        if (!this.get('boolean_no_project')){
            var avail_cpu = this.get('content').objectAt(this.get('selected_project_id')-1).get('cpu_av');
            if(avail_cpu === 0) this.set('alert_no_project_resources','Insufficient project resources for VRE server creation');
            return avail_cpu-selected_cpu_value;
        }
        return 0;
    }.property('selected_cpu_value','selected_project_id'),
    selected_project_cpu_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('cpu_choices') : [];
    }.property('selected_project_id'),
    selected_project_cpu_choices_available : function(){
        var cpu_choices = this.get('selected_project_cpu_choices');
        var available_cpu = Number(this.get('selected_project_available_cpu'));
        var selected_image = this.get('selected_image');
        var cpu_minimum = (!Ember.isEmpty(selected_image) && this.get('vreResourceMin')[selected_image]) && this.get('vreResourceMin')[selected_image]['cpu'] || 0;
        var cpu_choices_available = cpu_choices.map(function(item,index,original){
            return (Number(item)<=available_cpu && Number(item)>=cpu_minimum) && {value:item,disabled:false} || {value:item,disabled:true};
        },this);
        return cpu_choices_available;
    }.property('selected_project_cpu_choices.[]','selected_image'),
    selected_cpu_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_cpu_id')) ? 
        this.get('selected_project_cpu_choices')[this.get('selected_cpu_id')] : 
        this.set('selected_cpu_id',null) && '';
    }.property('selected_cpu_id','selected_project_id'),
    // RAM
    selected_project_available_ram : function(){
        var selected_ram_value = Ember.isEmpty(this.get('selected_ram_value')) ? 0 : Number(this.get('selected_ram_value'));
        this.set('alert_no_project_resources',null);
        if(!this.get('boolean_no_project')){
            var avail_ram = this.get('content').objectAt(this.get('selected_project_id')-1).get('ram_av');
            if(avail_ram === 0) this.set('alert_no_project_resources','Insufficient project resources for VRE server creation');
            return avail_ram-selected_ram_value;
        }
        return 0;
    }.property('selected_ram_value','selected_project_id'),
    selected_project_ram_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('ram_choices') : [];
    }.property('selected_project_id'),
    selected_project_ram_choices_available : function(){
        var ram_choices = this.get('selected_project_ram_choices');
        var available_ram = Number(this.get('selected_project_available_ram'));
        var selected_image = this.get('selected_image');
        var ram_minimum = (!Ember.isEmpty(selected_image) && this.get('vreResourceMin')[selected_image]) && this.get('vreResourceMin')[selected_image]['ram'] || 0;
        var ram_choices_available = ram_choices.map(function(item,index,original){
            return (Number(item)<=available_ram && Number(item)>=ram_minimum) && {value:item,disabled:false} || {value:item,disabled:true};
        },this);
        return ram_choices_available; 
    }.property('selected_project_ram_choices.[]','selected_image'),    
    selected_ram_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_ram_id')) ? 
        this.get('selected_project_ram_choices')[this.get('selected_ram_id')] : 
        this.set('selected_ram_id',null) && '';
    }.property('selected_ram_id','selected_project_id'),
    // DISK 
    selected_project_available_disk : function(){
        var selected_disk_value = Ember.isEmpty(this.get('selected_disk_value')) ? 0 : Number(this.get('selected_disk_value'));
        this.set('alert_no_project_resources',null);
        if (!this.get('boolean_no_project')){
            var avail_disk = this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_av');
            if(avail_disk === 0) this.set('alert_no_project_resources','Insufficient project resources for VRE server creation');
            return avail_disk-selected_disk_value;
        }
        return 0;
    }.property('selected_disk_value','selected_project_id'),
    selected_project_disk_choices : function(){
        return !this.get('boolean_no_project') ? this.get('content').objectAt(this.get('selected_project_id')-1).get('disk_choices') : [];
    }.property('selected_project_id'),
    selected_project_disk_choices_available : function(){
        var disk_choices = this.get('selected_project_disk_choices');
        var available_disk = Number(this.get('selected_project_available_disk'));
        var disk_choices_available = disk_choices.map(function(item,index,original){
            return Number(item)<=available_disk && {value:item,disabled:false} || {value:item,disabled:true};
        },this);
        return disk_choices_available; 
    }.property('selected_project_disk_choices.[]'),
    selected_disk_value : function(){
        return !this.get('boolean_no_project') && !Ember.isEmpty(this.get('selected_disk_id')) ? 
        this.get('selected_project_disk_choices')[this.get('selected_disk_id')] : 
        this.set('selected_disk_id',null) && '';
    }.property('selected_disk_id','selected_project_id'),
    /*
     * Utility Functions
     */
    category_from_image : function(that, image_name){
        var self = that; // get controller into self
        var arr_images = self.get('vreImages');
        for (i=0;i<arr_images.get('length');i++) {
            if (arr_images[i].get('image_name')==image_name) {
                return arr_images[i].get('image_category');
            }
        }
        return;
    },
    last_vre_popover_data : null,
    set_vre_popover_data : function(){
        if (!Ember.isEmpty(this.get('last_vre_server'))){
            var last_data = this.get('last_vre_server');
            var html_templ = '%@%@: <span class="text text-info pull-right">%@</span><br>';
            var html_snippet = '<h5 class="strong">Option: <span class="text text-info pull-right">Value</span></h5>';
            var category = this.get('category_from_image')(this, last_data.get('os_image'));
            html_snippet = html_templ.fmt(html_snippet, 'Project', last_data.get('project_name'));
            html_snippet = html_templ.fmt(html_snippet, 'Category', category);
            html_snippet = html_templ.fmt(html_snippet, 'Image', last_data.get('os_image'));
            html_snippet = html_templ.fmt(html_snippet, 'VRE Server Name', last_data.get('server_name'));
            html_snippet = html_templ.fmt(html_snippet, 'Storage', this.get('reverse_storage_lookup')[last_data.get('disk_template')]);
            html_snippet = html_templ.fmt(html_snippet, 'CPUs', last_data.get('cpu'));
            html_snippet = html_templ.fmt(html_snippet, 'RAM', last_data.get('ram'));
            html_snippet = html_templ.fmt(html_snippet, 'Disk Size', last_data.get('disk'));
            this.set('last_vre_popover_data',html_snippet);
        }else{
            this.set('last_vre_popover_data',null);
        }
    }.observes('last_vre_server'),
    // missing input block
    alert_input_missing_boundto : {
        // data column > alert message property, input control element id
        project_name : ['alert_missing_input_project','#id_project_id'],
        server_name : ['alert_missing_input_server_name','#id_server_name'],
        cpu : ['alert_missing_input_cpu','#id_cpu_choice'],
        ram : ['alert_missing_input_ram','#id_ram_choice'],
        disk : ['alert_missing_input_disk','#id_disk_choice'],
        disk_template : ['alert_missing_input_storage','#id_storage_choice'],
        os_image : ['alert_missing_input_image','#id_vre_image'],
        admin_password : ['alert_missing_input_admin_pass','#id_vre_admin_pass'],
        admin_email : ['alert_missing_input_admin_email','#id_vre_admin_email']
    },
    alert_input_missing_text : {
        // alert message property > message text
        alert_missing_input_project : 'Please select an ~okeanos project with sufficient resources',
        alert_missing_input_server_name : 'Please input a VRE server name',
        alert_missing_input_cpu : 'Please select CPU cores',
        alert_missing_input_ram : 'Please select RAM amount (MiB)',
        alert_missing_input_disk : 'Please select Disk size (GiB)',     
        alert_missing_input_storage : 'Please select a disk template',
        alert_missing_input_image : 'Please select VRE category/image',
        alert_missing_input_admin_pass : 'Please type in or generate an admin password. Copy it for first time login.',
        alert_missing_input_admin_email : 'Please input the admin e-mail'
    },
    missing_input : function(that, new_server){
        var self = that; // get the controller reference into self
        // clear alerts on new check
        for (alert in self.get('alert_input_missing_text')){
            self.set(alert,null);
        }
        for (property in new_server) {
            if (Ember.isEmpty(new_server[property])) {
                var alert_prop_name = self.get('alert_input_missing_boundto')[property][0];
                self.set(alert_prop_name,self.get('alert_input_missing_text')[alert_prop_name]);
                var input_element = $(self.get('alert_input_missing_boundto')[property][1]);
                window.scrollTo(input_element.offsetLeft, input_element.offsetTop);
                input_element.focus();
                return true;
            }
        }
        return false;
    },    
    missing_resources : function(that, new_server){
        var self = that; // get the controller reference into self
        // clear message on new check
        self.set('message',null);
        var missing_resources = self.get('selected_project_available_vm') < 1 || self.get('selected_project_available_ip') < 1;
        if (missing_resources) self.set('message','Insufficient project resources for VRE server creation');
        return missing_resources;
    },
    // invalid input block
    alert_input_invalid_boundto : {
        // data column > alert message property, input control element id
        admin_password : ['alert_invalid_input_admin_pass','#id_vre_admin_pass'],
        admin_email : ['alert_invalid_input_admin_email', '#id_vre_admin_email']
    },
    alert_input_invalid_text : {
        // alert message property > message text
        alert_invalid_input_admin_pass : '%@ Upper/lowercase letters and numbers allowed. Minimum length:8.',
        alert_invalid_input_admin_email: '%@ not a valid e-mail address. Example: admin@example.com'
    },
    alert_input_validators : {
        // model property > true for invalid input, false/null for valid
        admin_password : function(value,self){
            var alert_prop_name = self.get('alert_input_invalid_boundto')['admin_password'][0];
            var input_element = $(self.get('alert_input_invalid_boundto')['admin_password'][1]);
            var _invalidpattern = /[^a-zA-Z0-9]+/;
            var _minlength = 8;
            var _result = _invalidpattern.exec(value) || '';
            if (value.length < _minlength || _result.length > 0){
                var _alert_text = self.get('alert_input_invalid_text')[alert_prop_name];
                _result.length > 0 ? self.set(alert_prop_name,_alert_text.fmt('Invalid input:'+_result)) : self.set(alert_prop_name,_alert_text.fmt(''));
                window.scrollTo(input_element.offsetLeft, input_element.offsetTop);
                return true;
            }
            return false;
        },
        admin_email : function(value,self){
            var alert_prop_name = self.get('alert_input_invalid_boundto')['admin_email'][0];
            var input_element = $(self.get('alert_input_invalid_boundto')['admin_email'][1]);
            var _validpattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$/;
            var result = _validpattern.test(value);
            if (!result){
                var _alert_text = self.get('alert_input_invalid_text')[alert_prop_name];
                self.set(alert_prop_name,_alert_text.fmt(value));
                window.scrollTo(input_element.offsetLeft, input_element.offsetTop);
                return true;
            }
            return false;
        }
    },
    invalid_input : function(that, new_server){
        var self = that; // get the controller reference into self
        // clear alerts on new check
        for (alert in self.get('alert_input_invalid_text')){
            self.set(alert,null);
        }
        for (property in new_server) {
            if (!Ember.isEmpty(self.get('alert_input_validators')[property])){
                var invalid = self.get('alert_input_validators')[property](new_server[property],self);
                if (invalid) return true;
            }
        }
        return false;
    },
    /*
     * Actions
     */
    actions : {
        focus_project_selection : function(){
            $('#id_project_id').focus().fadeTo(700,0.4).fadeTo(300,1.0);
        },
        pick_storage : function(index, value){
            this.set('selected_storage_id',index);
            $('#id_storage_choice > label').removeClass("active btn-success");
            var selector = '#id_storage_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            this.set('alert_missing_input_storage',null);
        },
        pick_flavor : function(index, value){
            this.set('selected_flavor_id',index);
            $('#id_vre_flavors > label').removeClass("active btn-success");
            var selector = '#id_vre_flavors #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            var selected_flavor_data = this.get('vreFlavorData')[this.get('selected_flavor_id')];
            var cpu_index = this.get('selected_project_cpu_choices').indexOf(selected_flavor_data['cpu']);
            var ram_index = this.get('selected_project_ram_choices').indexOf(selected_flavor_data['ram']);
            var disk_index = this.get('selected_project_disk_choices').indexOf(selected_flavor_data['disk']);
            if (cpu_index >=0) this.send('pick_cpu',cpu_index,selected_flavor_data['cpu'],true);
            if (ram_index >=0) this.send('pick_ram',ram_index,selected_flavor_data['ram'],true);
            if (disk_index >=0) this.send('pick_disk',disk_index,selected_flavor_data['disk'],true);
        },
        select_matching_flavor : function(resource,value){
            var cpu = resource == 'cpu' && value || (this.get('selected_cpu_value') ||0);
            var ram = resource == 'ram' && value || (this.get('selected_ram_value') ||0);
            var disk = resource == 'disk' && value || (this.get('selected_disk_value') ||0);
            var selected = {'cpu':cpu,'ram':ram,'disk':disk};
            if (selected['cpu'] == 0 || selected['ram'] == 0 || selected['disk'] == 0){
                this.set('selected_flavor_id',null);
            }
            var flavor_data = this.get('vreFlavorData');
            for (i=0; i<flavor_data.length; i++){
                if (selected['cpu'] == flavor_data[i]['cpu'] && selected['ram'] == flavor_data[i]['ram'] && selected['disk'] == flavor_data[i]['disk']){
                    this.send('pick_flavor',i,this.get('vreFlavorLabels')[i]);
                    return;
                }
            }
            this.set('selected_flavor_id',null);
        },
        pick_cpu : function(index, value, from_flavor){
            this.set('selected_cpu_id',index);
            $('#id_cpu_choice > label').removeClass("active btn-success");
            var selector = '#id_cpu_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            if (!from_flavor) this.send('select_matching_flavor','cpu',value);
            this.set('alert_missing_input_cpu',null);
        },
        pick_ram : function(index, value, from_flavor){
            this.set('selected_ram_id',index);
            $('#id_ram_choice > label').removeClass("active btn-success");
            var selector = '#id_ram_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            if (!from_flavor) this.send('select_matching_flavor','ram',value);
            this.set('alert_missing_input_ram',null);
        },
        pick_disk : function(index, value, from_flavor){
            this.set('selected_disk_id',index);
            $('#id_disk_choice > label').removeClass("active btn-success");
            var selector = '#id_disk_choice #%@'.fmt(value);
            $(selector).addClass("active btn-success");
            if (!from_flavor) this.send('select_matching_flavor','disk',value);
            this.set('alert_missing_input_disk',null);
        },
        pick_server_name : function(){
            if (!Ember.isEmpty(this.get('vre_server_name'))){
                this.set('alert_missing_input_server_name',null);
            }
        },
        find_last_config : function(){
            var filter_by = ['DESTROYED','ACTIVE'];
            var self = this;
            var store = this.get('store');
            store.fetch('user',1).then(function(user){
                var vreservers = user.get('vreservers').get('content');
                var arr_filtered_servers = vreservers.filter(function(item,index,original){
                    return filter_by.contains(item.get('description_vre_status'));
                }).sortBy('action_date');
                self.set('last_vre_server',arr_filtered_servers.get('lastObject'));
            },function(reason){
                console.log(reason.message);
            });
        },
        apply_last_config : function(){
            var self = this;
            var project_id = null;
            if (!Ember.isEmpty(this.get('last_vre_server'))){
                var last_server = this.get('last_vre_server');
                project_id = this.get('content').findBy('project_name',last_server.get('project_name')).get('id');
                if (!Ember.isEmpty(project_id)){
                    this.set('selected_project_id',project_id);
                    var category = this.get('category_from_image')(this, last_server.get('os_image'));
                    this.set('selected_category',category);
                    Ember.run.later(function(){self.set('selected_image',last_server.get('os_image'));},100);
                    this.set('vre_server_name',last_server.get('server_name_noprefix'));
                    Ember.run.later(function(){
                        var cpu_index = self.get('selected_project_cpu_choices').indexOf(last_server.get('cpu'));
                        self.send('pick_cpu',cpu_index,last_server.get('cpu'));
                        var ram_index = self.get('selected_project_ram_choices').indexOf(last_server.get('ram'));
                        self.send('pick_ram',ram_index,last_server.get('ram'));
                        var disk_index = self.get('selected_project_disk_choices').indexOf(last_server.get('disk'));
                        self.send('pick_disk',ram_index,last_server.get('disk'));
                    },300);
                }
            }
        },
        admin_pass_generate : function(){
            this.set('vre_admin_pass',PassGen.generate(12));
            this.send('admin_pass_validate');
            this.send('admin_pass_select');
        },
        admin_pass_select : function(){
            if (!Ember.isEmpty(this.get('vre_admin_pass'))){
                Ember.run.later(function(){$('#id_vre_admin_pass').select();},100);
                this.set('alert_missing_input_admin_pass',null);
            }
        },
        admin_pass_validate : function(){
            this.set('alert_invalid_input_admin_pass',null);
            this.set('alert_missing_input_admin_pass',null);
            if (!Ember.isEmpty(this.get('vre_admin_pass'))) this.get('invalid_input')(this,{admin_password: this.get('vre_admin_pass')});
        },
        admin_email_validate : function(){
            this.set('alert_invalid_input_admin_email',null);
            this.set('alert_missing_input_admin_email',null);
            if (!Ember.isEmpty(this.get('vre_admin_email'))) this.get('invalid_input')(this,{admin_email: this.get('vre_admin_email')});
        },
        submit_create : function(){
            var that = this;
            var new_server = {};
            var extra_fields = this.get('vreImageExtraFields');
            for (model_property in this.get('model_to_controller_map')){
                var bound_controller_property = this.get('model_to_controller_map')[model_property];
                new_server[model_property] = this.get(bound_controller_property);
            }
            var image_extra_fields = (extra_fields['*'] || []).concat(extra_fields[new_server['os_image']] || []).uniq();
            for (image in extra_fields){// remove fields that are not applicable to selected image
                for (i=0;i<extra_fields[image].length;i++){
                    if (!image_extra_fields.contains(extra_fields[image][i])){
                        delete new_server[extra_fields[image][i]];
                    }
                }
            }
            if (this.get('missing_resources')(that, new_server)){
                return;
            }
            if (this.get('missing_input')(that, new_server)){
                return;
            }
            if (this.get('invalid_input')(that, new_server)){
                return;
            }
            this.store.fetch('user',1).then(function(user){
                //success
                var new_record = that.store.createRecord('uservreserver',new_server);
                new_record.save().then(function(data){
                    if (!Ember.isEmpty(data.get('admin_password'))){
                        var admin_pass_msg = {'msg_type': 'warning', 'msg_text': 'The admin password for %@ of \"%@%@\" VRE server is %@'.fmt(data.get('os_image'),'[orka]-',data.get('server_name'),data.get('admin_password'))};
                        that.get('controllers.userWelcome').send('addMessage',admin_pass_msg);
                    }
                    that.set('controllers.userWelcome.create_cluster_start', true);
                    that.get('controllers.userWelcome').send('setActiveTab','vreservers');
                    Ember.run.next(function(){that.transitionToRoute('user.welcome');});
                },function(reason){
                    console.log(reason);
                });
            },function(reason){
                //error
                console.log(reason);
            });
        },
        clear_cached : function(){// invalidate data cached on page, linked to selected project
            this.set('selected_storage_id',null);
            this.set('selected_cpu_id',null);
            this.set('selected_ram_id',null);
            this.set('selected_disk_id',null);
            this.set('selected_flavor_id',null);
            this.set('selected_category',null);
            this.set('selected_image',null);
            this.set('vre_server_name',null);
            this.set('vre_admin_pass',null);
            this.set('vre_admin_email',null);
            this.set('message',null);
            this.set('alert_no_project_resources',null);
        },
        reset : function(){ // invalidate selected project (data linked to project cascades)
            this.set('selected_project_id',null);
            this.set('vre_server_name',null);
            this.set('vre_admin_pass',null);
            this.set('vre_admin_email',null);
        },
        cancel : function(){
            var that = this;
            this.send('reset');
            this.get('controllers.userWelcome').send('setActiveTab','vreservers');
            Ember.run.next(function(){that.transitionToRoute('user.welcome');});
        }
    }
});
