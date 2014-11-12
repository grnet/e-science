 ##Selenium tests for Ember/Django App

To run the tests you need:

1. `pip install -U selenium` or `pip install selenium`

2. For all the selenium tests you will need an ~okeanos token which will be located in .config.txt file in <projectroot>/.private/ 

This is the format of the .config.txt file:

	[global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0
	
	token = YOUR ~okeanos TOKEN

	[cluster]
	
	master_ip = x.x.x.x (not needed for the selenium tests)
	
	[deploy]

	url = your deploy application url (eg for localhost http://127.0.0.1:8000/ or a public ip in ~okeanos (http://okeanos_public_ip:8000)) 
	

Of course you need to have a running django server in your [localhost:8000](localhost:8000) or a public one in ~okeanos where Selenium expects to reach the Ember/Django app.

Run the selenium tests either with `nosetests`, or separately with `python test_*`


