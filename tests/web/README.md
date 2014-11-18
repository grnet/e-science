##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For the login and logout tests you will need an ~okeanos token which will be located in .config.txt file in <projectroot>/.private/ this is the format of the file:

	[global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0

	token = YOUR TOKEN

	project_uuid = the e-science project uuid, needed for the ember_django  application to run

	[cluster]
	
	master_ip = x.x.x.x

	[deploy]

	url = your base url (eg for localhost http://127.0.0.1:8000/)

Run the selenium tests either with `nosetests`, or separately with `python test_*`
