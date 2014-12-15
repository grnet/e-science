module('Integration Tests - Routes', {
	setup: function(){
    	visit('/');
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
