How to install Webserver
--

This role can be executed as:

ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "choose_role=webserver webserver_ip=xxxxx"
Webserver_ip is the public ip address of the host we want to install Django and check the webserver.
Default value of webserver_ip is the ip address of the webserver host in the ansible_hosts file.

Giving values to variables from the command line is optional but necessary. Especially the following Webserver role variables [db_password, db_user, db_name, django_admin_name, django_admin_password] should always be given from command line when executing the playbook. If not given the playbook will run with the default settings which is not recommended.

So, the optimal execution of webserver role would be:

ansible-playbook -i [path/ansible_hosts] [path/ansible/site.yml] -e "db_password=xxxxx db_user=xxxxx db_name=xxxxx django_admin_name=xxxxx django_admin_password=xxxxx webserver_ip=xxxxx choose_role=webserver" 

