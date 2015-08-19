// Main application controller
// loggedIn, homeURL, adminURL, STATIC_URL
App.ApplicationController = Ember.Controller.extend({
    STATIC_URL : DJANGO_STATIC_URL,
    APP_VERSION : App.VERSION,
    // other controllers that need to be accessible from this one
    // for .set or .get
    needs : ['homepage', 'userLogin', 'userWelcome', 'clusterCreate', 'clusterManagement', 'helpImages', 'vreserverCreate', 'vreserverManagement', 'helpVreimages'],
    loggedIn : false,
    name_of_user : '',
    userTheme : user_themes,
    orkaImageData : {}, // stores raw OrkaImage data in object format
    vreImageData : {}, // stores raw VreImage data in object format
    user_name : function() {
        if (this.get('loggedIn')) {
            var that = this;
            this.store.find('user', 1).then(function(user) {
                that.set('name_of_user', user.get('user_name'));
                return user.get('user_name');
            });
        } else {
            return '';
        }
    }.property('loggedIn'),
    homeURL : function() {
        if (this.get('loggedIn')) {
            return "#/user/welcome";
        } else {
            return "#/";
        }
    }.property('loggedIn'),
    adminURL : function() {
        var admin_url = window.location.origin + "/admin";
        return admin_url;
    }.property(),
    
    // controller property for use on template to load OrkaImage and VreImage data to the store
    // application route activation > template render > sends refresh_*image_data action
    // which GET(s) the data to the store and controller.application.*ImageData.  
    dataLoader : function() {
        this.send('refresh_orkaimages_data');
        this.send('refresh_vreimages_data');
        return '';
    }.property(),
    
    // utility function for transforming OrkaImage data from object format to others
    dataTransformImages : function(images, strtype) {
        switch (strtype) {
        case "handlebars":
            var arrImages = Ember.makeArray(images);
            for (i=0;i<arrImages.length;i++){
                var components = JSON.parse(arrImages[i].get('image_components'));
                var arrComponents = [];
                for (k in components){
                    arrComponents.push({"name":k,"property":components[k]});
                }
                arrImages[i].set('image_components',arrComponents);
            }
            return arrImages;
            break;
        default:
            return images;
        }
    },

    actions : {
        change_theme : function(cssUrl) {
            var self = this;
            changeCSS(cssUrl, 0);
            // PUT user_theme to Django backend, when selected.
            if (cssUrl) {
                this.store.find('user', 1).then(function(user) {
                    user.set('user_theme', cssUrl);
                    self.store.push('user', self.store.normalize('user', {
                        'id' : 1,
                        'user_theme' : user.get('user_theme')
                    })).save();
                });
            }
        },
        // GET(s) orka image data from the backend.
        // On successful promise resolution [transform and] load to other controllers
        // for use on templates. Requires an orkaImages array to be set on other controllers
        // and populated from here.
        // It can then be referenced in templates as
        // {{#each image in orkaImages}}
        //   {{image.image_name}}{{image.image_pithos_uuid}}
        //     {{#each component in image.image_components}}{{component.name}}{{component.property.version}}{{component.property.help}}{{/each}}
        // {{/each}}
        refresh_orkaimages_data : function() {
            var that = this;
            this.store.fetch('orkaimage', {}).then(function(data) {
                that.set('orkaImageData', data.get('content'));
                var handlebarsData = that.get('dataTransformImages')(that.get('orkaImageData'),'handlebars');
                that.get('controllers.homepage').set('orkaImages', handlebarsData);
                that.get('controllers.userWelcome').set('orkaImages', handlebarsData);
                that.get('controllers.clusterManagement').set('orkaImages', handlebarsData);
                that.get('controllers.helpImages').set('orkaImages', handlebarsData);
                // decorate the model with an active_image property and set it to the first image loaded
                that.get('controllers.helpImages').send('setActiveImage', handlebarsData.objectAt(0).get('image_pithos_uuid'));
                that.get('controllers.clusterCreate').set('orkaImages', handlebarsData);
            }, function(reason) {
                console.log(reason.message);
            });
        },
        refresh_vreimages_data : function() {
            var that = this;
            this.store.fetch('vreimage', {}).then(function(data) {
                that.set('vreImageData', data.get('content'));
                var handlebarsData = that.get('dataTransformImages')(that.get('vreImageData'),'handlebars');
                that.get('controllers.homepage').set('vreImages', handlebarsData);
                that.get('controllers.userWelcome').set('vreImages', handlebarsData);
                that.get('controllers.vreserverManagement').set('vreImages', handlebarsData);
                that.get('controllers.helpVreimages').set('vreImages', handlebarsData);
                // decorate the model with an active_image property and set it to the first image loaded
                that.get('controllers.helpVreimages').send('setActiveImage', handlebarsData.objectAt(0).get('image_pithos_uuid'));
                that.get('controllers.vreserverCreate').set('vreImages', handlebarsData);
            }, function(reason) {
                console.log(reason.message);
            });
        }
    }
});
