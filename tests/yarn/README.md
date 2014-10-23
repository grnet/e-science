##Run pi test for yarn cluster

To run the test you need:

1. To create or already have an active yarn cluster.
2. The script needs the master node's ip to run which will be located in .master_ip file in <projectroot>/.private/

    [cluster]
    master_ip = x.x.x.x

Run pi test with either with `nosetests`, or  with `python test_run_pi.py`
