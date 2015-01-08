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

orka wrapper tests
------------------
The test for checking orka wrapper is the bash script test_create_bare_vm.sh. It creates and connects to a bare vm in ~okeanos 
and then it installs and setup all required software for orka wrapper to be functional. Afterwards, the user can ssh connect to the vm, run

    . ~/.virtualenvs/orkaenv/bin/activate
    
 
and then orka commands can be executed, e.g. orca -h.  The bash script requires two arguments, the project id, in which the vm will be created, and the github repo which will be cloned.


A user can check the existing projects and their respective ids with: 

    kamaki project list

and run the bash script with
        
        . test_create_bare_vm.sh <project_id> <git repo uri>