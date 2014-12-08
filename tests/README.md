##Mock test for bare cluster

To run the test you need:

1. `pip install mock`

2. Test scripts needs some additional information inside a file          `<project>/.private/.config.txt` with the following format:

        [global]
        default_cloud = ~okeanos

        [cloud "~okeanos"]
        url = https://accounts.okeanos.grnet.gr/identity/v2.0
        token = <YOUR TOKEN>
        project_id = the e-science project id, needed for the ember_django application to run

        [cluster]
        master_ip = x.x.x.x  (to be used in run_pi_yarn on an existing cluster)

        [deploy]
        url = your web server base url (eg for localhost http://127.0.0.1:8000/, not necessary for testing) 

        [project]
        name = the name of the ~okeanos project you want to run your tests into


Run mock test with either with `nosetests`, or  with `python test_create_cluster.py`
