#Orka service

Orka service is provided by a personal Orka server. Every ~okeanos user can build a personal Orka server by following the instructions [here](#create-personal-orka-server-in-okeanos-for-users).


## Create ~okeanos image for personal Orka server (for administrators)

The python script deploy_orka_server.py can be used either for creating an ~okeanos Orka server image
or starting an Orka server created by such an image. Before using the script as image creator, the following packages must be installed
(tested in Debian 8 ~okeanos bare image):

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y python python-dev gcc 
    wget https://bootstrap.pypa.io/get-pip.py;
    sudo python get-pip.py
    sudo pip install kamaki
    sudo pip install ansible

**Important**: a public ssh key must exist locally as ~/.ssh/id_rsa.pub. If not, the python script will exit.

Clone the e-Science project and run the python script:

    git clone <escience git repo>
    cd <project_root>/deploy/
    python deploy_orka_server.py create --name=orka_image --flavor_id=~okeanos_flavor_number --project_id=~okeanos_project_id --image_id=~okeanos_debian_image_id --git_repo=project_repo_in_github --git_repo_version=version_or_branch_of_repo --token=~okeanos_token

This will create a virtual machine in ~okeanos and install everything that is needed for the orka server to function with Debian 8.2 but without configuring sensitive parameters and passwords.
After VM becomes active, the admin/image-creator can ssh to the virtual machine and after removing authorized_keys files:

    rm /root/.ssh/authorized_keys
    rm /home/orka_admin/.ssh/authorized_keys

run:

    snf-mkimage --public --print-syspreps -f -u name_of_Orka_server_image -t ~okeanos_token -a auth_url -r name_of_Orka_server_image /

After snf-image-creator finishes, the image will be ready for building Orka servers.
More information about the software that is installed for the creation of the image can be found in the following Ansible playbooks:

    deploy/setup_orka_admin.yml
    deploy/roles/webserver/tasks/main.yml


## Create personal Orka server in ~okeanos (for users)

Users should read the following section, regarding Orka server requirements, before starting the creation of their personal Orka server.

###Orka server Flavor Requirements

Minimum Requirements: 1 CPU, 1 GB of Ram and 5 GB of disksize.

Recommended: 2 CPUs, 2 GB of Ram and 10 GB of disksize.

Number of CPUs dictate the amount of long running tasks the Orka server execute at the same time. With 1 cpu for example, a user will not be able to build two different Hadoop clusters at the same time. 

### Create and start Orka server

User creates a virtual machine in ~okeanos with Orka Server-on-Debian 8 image, then:

    ssh root@virtual_machine_public_ip
    passwd orka_admin
    su - orka_admin
    cd projects/e-science/deploy

The python script that starts the Orka server reads critical information from a user-created yaml file.
In deploy directory there is a sample file (deploy_sample_file.yml) which can be used as a template for the user-created deploy yaml file.
A user can do (inside projects/e-science/deploy):

    cp deploy_sample_file.yml <user_created_yaml_file>.yml
    nano <user_created_yaml_file>.yml

and then edit the file:

    # Password of system user orka_admin
    orka_admin_password: <the linux password of orka_admin user. It is the password the user gave before, when ran passwd orka_admin>
    # Django admin password
    django_admin_password: <A password at least 8 characters long for administrator login in Orka server>
    # Password of postgresql user
    postgresql_password: <A password at least 8 characters long for postgresql database>
    # The okeanos uuid of the user who will login in the orka gui
    okeanos_user_uuid: <~okeanos_user_uuid. Below follows info on how to find the uuid> 

Users can find their unique ~okeanos_user_uuid from ~okeanos [webpage](https://accounts.okeanos.grnet.gr/ui/api_access).It is under `username` in Other clients section.

Alternatively, by running:

    kamaki user info
    
in an environment that kamaki is [set up](https://www.synnefo.org/docs/kamaki/latest/installation.html).

Finally, after done editing the user-created yml file, run the deploy script:

    python deploy_orka_server.py start <path_to_user_created_yaml_file>

When python script finishes successfully, user can open in a browser the public IP of Orka server and start using the Orka services.


### Example of starting a personal Orka server

After creation of a virtual machine in ~okeanos with Orka Server-on-Debian 8 image, then:

    ssh root@12.345.678.123
    passwd orka_admin
    
give `orkaadmintestpassword` as password when asked, then:

    su - orka_admin
    cd projects/e-science/deploy
    cp deploy_sample_file.yml examplefile.yml
    nano examplefile.yml

and then edit examplefile.yml:

    # Password of system user orka_admin
    orka_admin_password: orkaadmintestpassword
    # Django admin password
    django_admin_password: adminloginstrongpassword
    # Password of postgresql user
    postgresql_password: reallystrongpasswordyes
    # The okeanos uuid of the user who will login in the orka gui
    okeanos_user_uuid: b691ecsfg-1gfe-4ekf-b6en-87u6f73eeaaa 


and run the deploy script:

    python deploy_orka_server.py start examplefile.yml


### Example of restarting a personal Orka server

After starting an Orka server, the deploy_orka_server.py script can be used for restarting the server, in case of an error or after
an update. User must access the server:

    ssh root@orka_server_ip
    su - orka_admin
    cd projects/e-science/deploy
    
and run the python script again with restart argument and the deploy file used for starting the server.
**In case of deletion of the deploy file used in starting the orka server**, user must create it again but now the only mandatory entry in the file
is the `orka_admin_password`. So, a user creates the file:

    nano examplefile.yml

and adds only the following entry:

    # Password of system user orka_admin
    orka_admin_password: <orka_admin linux password e.g. orkaadmintestpassword>


If the user have kept his deploy file used in starting the server, he can use it again for restarting or updating the server.
In any case, Orka server will be restarted with the following command:

    python deploy_orka_server.py restart examplefile.yml


### Example of updating a personal Orka server

Users can update their personal Orka servers, if there are updates in main e-Science github repo, by running the python script
deploy_orka_server.py with the update argument and the deploy file used for starting the server. If the deploy file was deleted,
the user must create it again, as shown in [restarting the server section](#example-of-restarting-a-personal-orka-server).

So, for updating the server, the following steps are required:

    ssh root@orka_server_ip
    su - orka_admin
    cd projects/e-science/deploy
    
and run the script:

    python deploy_orka_server.py update examplefile.yml

after the update is done, server should be restarted with:

    python deploy_orka_server.py restart examplefile.yml
    
The default github repo that deploy_orka_server.py will look for updates is https://github.com/grnet/e-science.git and the master branch.