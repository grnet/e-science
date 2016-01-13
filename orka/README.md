#Orka service

Orka service is deployed and accessed by a personal Orka server. Every ~okeanos user can build a personal Orka server by following the instructions [here](#create-a-personal-orka-server-in-okeanos-for-users).


## Create ~okeanos image for personal Orka server (for administrators)

Creating an Orka image or starting an Orka server by such an image is performed through the python script `deploy_orka_server.py`. Before using the script as image creator, the following packages must be installed
(tested in a VM from an Debian 8.x ~okeanos bare image):

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y python python-dev gcc 
    wget https://bootstrap.pypa.io/get-pip.py;
    sudo python get-pip.py
    sudo pip install kamaki
    sudo pip install ansible

**Important**: a public ssh key must exist locally in file `~/.ssh/id_rsa.pub`. If not, the python script will exit.

Clone the e-Science project and run the python script:

    git clone <escience git repo>
    cd <project_root>/deploy/
    python deploy_orka_server.py create --name={{orka_image}} --flavor_id={{~okeanos_flavor_number}} --project_id={{~okeanos_project_id}} --image_id={{~okeanos_debian_image_id}} --git_repo={{project_repo_in_github}} --git_repo_version={{version_or_branch_of_repo}} --token={{~okeanos_token}}

This will create a virtual machine in ~okeanos and install everything that is needed for the orka server to function with Debian 8.2, but without configuring sensitive parameters and passwords.
After VM becomes active, the admin/image-creator should ssh to the virtual machine and after removing authorized_keys files:

    rm /root/.ssh/authorized_keys
    rm /home/orka_admin/.ssh/authorized_keys

run:

    snf-mkimage --public --print-syspreps -f -u {{name_of_Orka_server_image}} -t {{~okeanos_token}} -a {{auth_url}} -r {{name_of_Orka_server_image}} /

After snf-image-creator finishes, the image will be ready for building Orka servers.
More information about the installed software for the creation of the image can be found in the following Ansible playbooks:

    deploy/setup_orka_admin.yml
    deploy/roles/webserver/tasks/main.yml

### Example of creating an ~okeanos image for personal Orka server

Assuming the administrator's Linux working environment is ~okeanos Debian Base 8.2 without a pair of SSH keys, the following steps can be executed as `root` or as a user with sudo privileges:

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y python python-dev gcc 
    wget https://bootstrap.pypa.io/get-pip.py;
    sudo python get-pip.py
    sudo pip install kamaki
    sudo pip install ansible
    ssh-keygen -t rsa (rest of the arguments can be left to default)

Clone the e-Science project and run the python script (supply your own project_id, image_id, flavor_id, token; all of these can be retrieved through respective `kamaki` commands):

    git clone https://github.com/grnet/e-science.git
    cd e-science/deploy/
    python deploy_orka_server.py create --name=orka_image_vm --flavor_id=39 --project_id=11aaaaa1-11dd-11ae-a11e-a1a211111111 --image_id=a1111aa1-1aa1-1aa1-aa11-aaaa111a11aa --git_repo=https://github.com/grnet/e-science.git --git_repo_version=master --token=AAa1aAaAAA1a1A1ABA1AA1aAAaa1aaaaaaaa11_111a

This will create a virtual machine in ~okeanos and install everything that is needed for the server to provide the Orka services. Wait until the VM becomes active, and do the following in order to 'burn' it as an ~okeanos public image:

    ssh root@{{virtual_machine_public_IPv4}}

As the root user now of {{virtual_machine_public_IPv4}}:

    rm /root/.ssh/authorized_keys
    rm /home/orka_admin/.ssh/authorized_keys
    snf-mkimage --public --print-syspreps -f -u Orka_on_Debian_8_image -t AAa1aAaAAA1a1A1ABA1AA1aAAaa1aaaaaaaa11_111a -a https://accounts.okeanos.grnet.gr/identity/v2.0 -r Orka_on_Debian_8_image /

After snf-image-creator is finished, the new image can be used for the creation of Orka servers.


## Create a personal Orka server in ~okeanos (for users)

You should read the following section regarding Orka server requirements, before starting the creation of your personal Orka server.

#### Orka server Hardware Requirements

Minimum Requirements: 1 CPU, 1 GB RAM and 5 GB for disk size.

Recommended: 2 CPUs, 2 GB RAM and 10 GB for disk size.

Number of CPUs dictate the amount of long running tasks the Orka server executes at the same time. With 1 CPU for example, a user will not be able to build two different Hadoop clusters at the same time. 

### Create and start personal Orka server

You create a  new virtual machine in ~okeanos based on "Personal Orka Server" image, with a public IPv4 attached, and then access the new VM, alter the orka_admin password, by typing the following CLI commands:

    ssh root@{{virtual_machine_public_IPv4}}

As the root user now of {{virtual_machine_public_IPv4}}:

    passwd orka_admin
    su - orka_admin

As the orka_admin  user now of {{virtual_machine_public_IPv4}}:

    cd projects/e-science/deploy

The python script that starts the Orka server reads critical information from a user-created yaml file.
In the `deploy` directory there is a sample file, `deploy_sample_file.yml`, which can be used as a template for your own deploy yaml file.
You can copy the template file (inside projects/e-science/deploy):

    cp deploy_sample_file.yml <user_created_yaml_file>.yml
    nano <user_created_yaml_file>.yml

and then edit the file, to provide your own configuration information:

    # Password of system user orka_admin
    orka_admin_password: <the Linux password of orka_admin user. It is the password the user gave just after the first ssh before, when ran passwd orka_admin>
    # Django admin password
    django_admin_password: <A password at least 8 characters long for administrator login in Orka server>
    # Password of postgresql user
    postgresql_password: <A password at least 8 characters long for postgresql database>
    # The okeanos uuid of the user who will login in the orka gui
    okeanos_user_uuid: <~okeanos_user_uuid. Below follows info on how to find the uuid> 

You can find yout unique ~okeanos_user_uuid from ~okeanos [webpage](https://accounts.okeanos.grnet.gr/ui/api_access). It is under `username` in Other clients section.

Alternatively, you can retrieve it by running `kamaki user info` in an environment with kamaki [set up](https://www.synnefo.org/docs/kamaki/latest/installation.html).

Finally, after done editing your yml file, run the deploy script:

    python deploy_orka_server.py start <path_to_user_created_yaml_file>

**Important note**: The script will prompt you to make sure you have a backup of all of the configuration values, because it will delete the yaml file, as a security measure.

When python script finishes successfully, you can open in a browser the https://{{virtual_machine_public_IPv4}} address and start using the Orka services.


### Example of restarting a personal Orka server

After starting an Orka server, the deploy_orka_server.py script can be used for restarting the server, in case of an error or an update. After accessing the server:

    ssh root@{{orka_server_ip}}
    su - orka_admin
    cd projects/e-science/deploy
    
and run the python script again with the 'restart' argument and the deploy file used for starting the server.

**In case of deletion of the deploy file used in starting the orka server**, you must create it again but now the only mandatory entry in the file
is the `orka_admin_password`. This is done by creating the file:

    nano examplefile.yml

and add only the following entry:

    # Password of system user orka_admin
    orka_admin_password: <orka_admin linux password e.g. orkaadmintestpassword>


If you kept your deploy file used in starting the server, the same file can be used again for restarting or updating the server.
In any case, Orka server will be restarted with the following command:

    python deploy_orka_server.py restart examplefile.yml


### Example of updating a personal Orka server

You can update your personal Orka server, (e.g, if there are updates in the main e-Science github repo), by running the python script
`deploy_orka_server.py` with the 'update' argument and the deploy file used for starting the server. If the deploy file was deleted,
you must create it again, as shown in [restarting the server section](#example-of-restarting-a-personal-orka-server).

So, for updating the server, the following steps are required:

    ssh root@{{orka_server_ip}}
    su - orka_admin
    cd projects/e-science/deploy
    
and run the script:

    python deploy_orka_server.py update examplefile.yml
  
The default github repo that deploy_orka_server.py will look for updates is `https://github.com/grnet/e-science.git` at the master branch.
The github repo and branch/version is set in `e-science/deploy/group_vars/webserver.yml` file and can be changed to point to another location.
