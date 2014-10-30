##Run pi test for yarn cluster

To run the test you need:

1. To create or already have an active yarn cluster.

2. The script needs the master node's ip to run which will be located in .config.txt file in <projectroot>/.private/ this is the format of the file:

	[global]

	default_cloud = ~okeanos

	[cloud "~okeanos"]

	url = https://accounts.okeanos.grnet.gr/identity/v2.0
	token = YOUR TOKEN

	[cluster]
	
	master_ip = x.x.x.x


Run pi test with either with `nosetests`, or  with `python test_run_pi.py`
