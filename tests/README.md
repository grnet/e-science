##Mock test for bare cluster

To run the test you need:

1. `pip install mock`

2. Test scripts needs some additional information inside a file          `<project>/.private/.config.txt` with the following format:

        [global]
        default_cloud = ~okeanos

        [cloud "~okeanos"]
        url = https://accounts.okeanos.grnet.gr/identity/v2.0
        token = <YOUR TOKEN>

        [cluster]
        master_ip = xx.xxx.xxx.xxx  (e.g. 83.212.111.222, to be used in run_pi_yarn and test_orka_cli_put_get on an existing cluster)

        [deploy]
        url = your web server base url (eg for localhost http://127.0.0.1:8000/, not necessary for testing) 

        [project]
        name = the name of the ~okeanos project you want to run your tests into


Unit and functional tests in **test_orka_cli_put_get.py** require an active hadoop cluster with **.kamakirc** file in master VM's /home/hduser path and orka-cli user's ssh pub key copied in hduser's
authorized_keys file. It is created automatically with latest orka build, no need for any orka-cli user additional action. Run them with `nosetests test_orka_cli_put_get.py`


The mock **test_create_cluster** can be run either with `nosetests test_create_cluster.py`, or  with `python test_create_cluster.py`

orka wrapper test in bare VM
----------------------------
The test for checking orka wrapper is the bash script test_orka_bare_VM.sh. It creates and connects to a bare VM in ~okeanos 
and then it installs and setup all required software for orka wrapper to be functional. Afterwards, the user can ssh connect to the VM, run

    . ~/.virtualenvs/orkaenv/bin/activate
    
 
and then orka commands can be executed, e.g. orka -h, orka create 'arguments'.  The bash script requires two arguments, the id of the project from which resources will be pulled for the VM creation, and the github repository to be cloned and used for the orka CLI.


A user, assuming they have installed and configured kamaki, can check their existing projects and the respective ids with: 

    kamaki project list
    
and run the bash script, after changing directory to [name_of_project_cloned_from_git]/tests/, with:
        
        . test_orka_bare_VM.sh  <project_id>  <git repo uri>
        

If kamaki is not installed or configured, check [kamaki documentation] [kamaki_link]

[kamaki_link]: https://www.synnefo.org/docs/kamaki/latest/