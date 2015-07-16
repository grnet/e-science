##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For the tests you will need an ~okeanos token which is located in .config.txt file in <projectroot>/.private/ folder. This is the format of the file:

	[global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0

	token = YOUR TOKEN

	project_id = the e-science project id, needed for the webapp  application to run

	[cluster]
	
	master_ip = x.x.x.x

	[deploy]

	url = your base url (eg for localhost http://127.0.0.1:8000/)
	
	[project]
	
	name = the name of the project you want to run

Run the selenium tests either with `nosetests`, or separately with `python test_*`
