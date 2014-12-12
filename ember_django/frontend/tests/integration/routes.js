module('Integration Tests - Routes', {
	setup: function(){
	},
	teardown: function() {
    	App.reset();
    	// phantomjs seems to keep localstorage cache between tests, leads to false positives
    	localStorage.clear(); 
	}
});

test('root_route_redirects_to_homepage', function() {
  expect(1); // Ensure that we will perform one assertion

  visit('/');
  // Wait for asynchronous helpers above to complete
  andThen(function() {
    equal(currentRouteName(), 'homepage');
  });
});

test('protected_resources_redirect_to_login', function() {
  expect(2);
  visit('/cluster/create');
  andThen(function() {
    equal(currentRouteName(), 'user.login');
  });
  visit('/user/welcome');
  andThen(function() {
    equal(currentRouteName(), 'user.login');
  });
});

// this test errors (clicking submit causes it to restart)
test('login_successfully_redirects_to_welcome', function() {
	expect(1);
	visit('/user/login');
	andThen(function() {
		fillIn('#token', 'PLACEHOLDER'); // needs an active access token if not faked
		click('#id_login_submit_button');
		equal(currentRouteName(), 'user.welcome');
	});
});