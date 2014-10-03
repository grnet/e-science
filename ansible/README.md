How to run the Ansible playbook
---

This Ansible playbook has two distinct roles: 
 - yarn. Install and configure hadoop-2.5.1 yarn on ~okeanos cluster.
 - webserver. Install and setup Django, PostgreSql and celery on a okeanos virtual machine.

and one common for all hosts:
 - commons. Update, install sudo and fix missing locale for every host.

How to run yarn role
--
Choice of role must be given as argument from command line or else playbook wont run. For example
ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=yarn" will run
the playbook role yarn. As a default, it wont start its daemons or format the cluster.

If these functions are wanted, it can be enabled with variable [start_yarn=True]. Also, if it is run
for the first time, the yarn cluster needs formating so the variable format should be  [format=True].

For example, ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=yarn start_yarn=True format=True"
will install and configure yarn cluster,format it and start its daemons.

We can change the hadoop yarn version the playbook installs
by giving a different value to variable [yarn_version]. Default value is hadoop-2.5.1.

How to run webserver role
--

This role can be executed as:

ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=webserver create_djuser=True"

The [create_djuser=True] is needed the first time we run webserver role because it creates the djuser that is needed in
install and setup of the Django webserver.

Giving values to other webserver variables is optional but necessary. Especially the following Webserver role variables [db_password, db_user, db_name, django_admin_name, django_admin_password, djuser_password, ansible_sudo_pass] should always be given from command line or in the all.yml and webserver.yml files in group_vars folder. 

If not given the playbook will run with the default settings which is not recommended.
The [djuser_password] encrypted value is created by the user with [python -c 'import crypt; print crypt.crypt("mypassword", "$1$SomeSalt$")'] and
the ansible_sudo_pass is the unecrypted [djuser_password] value.

So, the optimal execution of webserver role for the first time from thecommand line would be:

ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "db_password=xxxxx db_user=xxxxx db_name=xxxxx django_admin_name=xxxxx django_admin_password=xxxxx choose_role=webserver create_djuser=True djuser_password=encrypted(dj_user password) ansible_sudo_pass=dj_user password"

It is easier though to change the default values in the ansible/group_vars/all.yml and ansible/group_vars/webserver.yml and run 
ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=webserver create_djuser=True"

Also, the variables [myprojectdir] [myprojectname] are the directory name where django projects will be created and a django project name and can be changed from their default values.





