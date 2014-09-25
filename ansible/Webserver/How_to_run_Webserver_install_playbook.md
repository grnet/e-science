How to run the Webserver install.yml
--

The playbook can be executed as:

ansible-playbook -i [path/ansible_hosts] [path/Webserver/install.yml] -e "public_ip=xxxxx"
public_ip is the public ip address of the host we want to install Django and check the webserver.

Giving values to variables from the command line is optional but necessary. Especially the following Webserver install playbook variables [password_db, db_user, db_name, admin_django_name, password_admin_django] should always be given from command line when executing the playbook. If not given, the playbook will run with the default settings.

So, the optimal execution of install playbook would be:

ansible-playbook -i [path/ansible_hosts] [path/Webserver/install.yml] -e "password_db=xxxxx db_user=xxxxx db_name=xxxxx admin_django_name=xxxxx password_admin_django=xxxxx public_ip=xxxxx"

