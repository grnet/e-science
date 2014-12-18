moduleFor('controller:application', 'Unit Tests - Controllers', {
	setup: function(){
		visit('/');
	},
	teardown: function(){
		App.reset();
		// phantomjs seems to keep localstorage cache between tests, leads to false positives
    	localStorage.clear(); 
	}
});

test('home_controller_starts_in_logged_out_state', function() {
  expect(1);

  var ctrl = this.subject();

  equal(ctrl.get('loggedIn'), false);
});

moduleFor('controller:application', 'Home Controller', {
	setup : function() {
		visit('/');
	},
	teardown : function() {
		App.reset();
	}
});

// this test group errors
moduleFor('controller:userLogin', 'Login test', {
	setup : function() {
		visit('/user/login');
	},
	teardown : function() {
		App.reset();
		// phantomjs seems to keep localstorage cache between tests, leads to false positives
    	localStorage.clear();
	},
	needs: ['controller:application']
});

// test framework disables the run-loop, we need to refactor relevant code IN APP with Ember.run()
// before we can proceed with mocking responses
test('controller: successfull_login_routes_to_welcome', function() {
	expect(1);

	// get the controller instance
	var ctrl = this.subject();
	// ctrl.set ('isLoggedIn' , true);
	// ctrl.set ('target' , 'user.login');
	// ctrl.transitionToRoute('user.welcome');

	ctrl.store = App.__container__.lookup('store:main');
	
	ctrl.send('login', 'PLACEHOLDER'); // needs to be replaced with an active access token if ajax not mocked
	andThen(function() {
		equal(currentRouteName(), 'user.welcome');
	});

});
