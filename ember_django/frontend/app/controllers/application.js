// Main application controller
// loggedIn, homeURL, adminURL, STATIC_URL
App.ApplicationController = Ember.Controller.extend({
    STATIC_URL : DJANGO_STATIC_URL,
    needs : ['userWelcome', 'homepage'],
    loggedIn : false,
    name_of_user : '',
    userTheme : user_themes,
    orkaImageData : {},

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
    // property for use on 
    dataLoader : function() {
        this.send('refresh_orkaimages_data');
        return '';
    }.property(),
    
    dataTransformImages : function(images, strtype) {
        switch (strtype) {
        case "array":
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
            return obj;
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
        refresh_orkaimages_data : function() {
            var that = this;
            this.store.fetch('orkaimage', {}).then(function(data) {
                that.set('orkaImageData', data.get('content'));
                that.get('controllers.homepage').set('orkaImages', that.get('dataTransformImages')(that.get('orkaImageData'),'array'));
            }, function(reason) {
                console.log(reason.message);
            });
        },
    }
});
