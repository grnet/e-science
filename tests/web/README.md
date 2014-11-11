##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For the login and logout tests you will need an ~okeanos token which will be located in .config.txt file in <projectroot>/.private/ this is the format of the file:

	[global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0
	token = YOUR TOKEN

	[cluster]
	
	master_ip = x.x.x.x

Run the selenium tests either with `nosetests`, or separately with `python test_*`
