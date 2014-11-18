##Mock test for bare cluster

To run the test you need:

1. `pip install mock`

2. The script needs the auth_url and token from okeanos those are located in a file inside         `<project>/.private/.config.txt `the file has the following format:

    [global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0
	token = YOUR TOKEN
	project_uuid = the e-science project uuid, needed for the ember_django  application to run
	[cluster]
	
	master_ip = x.x.x.x


Run mock test with either with `nosetests`, or  with `python test_create_bare_cluster.py`
