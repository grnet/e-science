##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For the login and logout tests you will need an ~okeanos token which will be located in .kamakirc file in <projectroot>/.private/ this is the format of the file:

    [global] 
    default_cloud = ~okeanos

    [cloud "~okeanos"]
    url = okeanos url
    token = Your token

3. Also (for the moment) you need to have a running server in your [localhost:8000](localhost:8000) where Selenium expects to reach the Ember/Django app.

Run the selenium tests either with `nosetests`, or separately with `python test_*`
