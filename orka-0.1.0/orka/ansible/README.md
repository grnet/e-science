How to run the Ansible playbook
---

This Ansible playbook has two distinct roles: 
 - yarn. Install and configure hadoop-2.5.2 yarn on ~okeanos cluster.
 - webserver. Install and setup a Django webserver running our ember application on a ~okeanos virtual machine.

and one common for all hosts:
 - commons. Install sudo and fix missing locale for every host.

How to run yarn role
--
Before running an Ansible playbook for a bare vm in ~okeanos, following commands must be executed in the bare vm:

    apt-get update
    apt-get install -y python
Choice of role must be given as argument from command line or else playbook wont run. For example

    ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=yarn"

will run the playbook role yarn. As a default, it wont start its daemons or format the cluster.

If these functions are wanted, it can be enabled with variable [start_yarn=True]. Also, if it is run
for the first time, the yarn cluster needs formating so the variable format should be  [format=True].

For example, 

    ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=yarn start_yarn=True format=True"
will install and configure yarn cluster,format it and start its daemons.

We can change the hadoop yarn version the playbook installs
by giving a different value to variable [yarn_version]. Default value is hadoop-2.5.2.

How to run webserver role
--

This role can be executed as:

    ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=webserver create_orca_admin=True"

The [create_orca_admin=True] is needed the first time we run webserver role because it creates the orca_admin user that is needed in
install and setup of the Django webserver.

Giving values to other webserver variables is optional but necessary. Especially the following Webserver role variables 

    [db_password, db_user, db_name, django_admin_name, django_admin_password, orca_admin_password, ansible_sudo_pass] 
    
should always be given from command line or in the all.yml and webserver.yml files in group_vars folder. 

If not given, the playbook will run with the default settings which is not recommended.
The [orca_admin_password] encrypted value is created by the user with 

    [python -c 'import crypt; print crypt.crypt("mypassword", "$1$SomeSalt$")'] 

and the ansible_sudo_pass is the unecrypted [orca_admin_password] value.

So, the optimal execution of webserver role for the first time from the command line would be:

    ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "db_password=xxxxx db_user=xxxxx db_name=xxxxx django_admin_name=xxxxx django_admin_password=xxxxx choose_role=webserver create_orca_admin=True orca_admin_password=encrypted(orca_admin_password) ansible_sudo_pass=orca_admin_password"

It is easier though to change the default values in the ansible/group_vars/all.yml and ansible/group_vars/webserver.yml and run 

    ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=webserver create_orca_admin=True"

Also, the variables [myprojectdir] [myprojectname] are the directory name where django projects will be created and a django project name and can be changed from their default values.

Other useful variables are :
- [escience_repo], which is the github repo from where webserver role will clone the django project. Default is gtzelepis.

- [path_to_folder_to_minify], which is the path of the app folder to minify/uglify the .js files.

- [path_to_folder_to_removelogging], which is the path of the app folder to removelogging the .js files	
