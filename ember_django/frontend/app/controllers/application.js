// Main application controller
// loggedIn, homeURL, adminURL, STATIC_URL
App.ApplicationController = Ember.Controller.extend({
    STATIC_URL : DJANGO_STATIC_URL,
    needs : 'userWelcome',
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
    dataLoader : function(){
        this.send('refresh_orkaimages_data');
        return '';
    }.property(),
    
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
                that.set('orkaImageData',data.get('content'));
            }, function(reason) {
                console.log(reason.message);
            });
        },
    }
}); 