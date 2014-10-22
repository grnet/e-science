##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For the login and logout tests you will need an ~okeanos token which will placed in a file named `token_file`

3. Also (for the moment) you need to have a running server in your [localhost:8000](localhost:8000) where Selenium expects to reach the Ember/Django app.

Run the selenium tests either with `nosetests`, or separately with `python test_*`
