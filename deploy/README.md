# Deploy Orka Server
A collection of python and ansible scripts have been assembled in `<project_root>/deploy` to facilitate the deployment of a specific version of the application.  
The environment consists of a standalone Virtual Machine running a release configuration with the Nginx-uWSGI-Postgres stack, serving the application from a public IP.
For more information check the e-science/orka/README.md file.

## Ansible playbooks

Below are available in tables, the ansible deploy webserver files and folders with their corresponding description:

|    File     | Description
|------------ |:---
|  group_vars/webserver.yml |  It includes constants and default values for variables used by webserver playbook.
|  roles      |  It includes the Ansible roles: webserver and commons and their corresponding subfolders.
|  staging.yml   |  It is the entry point of Ansible webserver playbook and distributes the Ansible tasks based on the input arguments.
|  setup_orka_admin.yml    | It is called when deploy_orka_server.py is used with argument create. Installs on an empty ~okeanos VM all the software packages needed for personal orka server to function.
|  deploy_sample_file.yml    | Example file, used as a template for the user-created YAML file that contains the mandatory passwords needed for the personal orka server to start.
|  deploy_orka_server.py | Python script that calls the ansible webserver playbook. 
|  ansible.cfg     | Ansible configuration file.


 In the case of *webserver* role, there are three subfolders, whose description is available below:

|    File     | Description
|------------ |:---
|    files    |  It includes the files that are necessary for the execution of specific services. They are transferred unchanged to the remote or local machine where commands from the ansible playbooks are executed
|    tasks/main.yml    |  It is called from deploy_orka_server.py script for various tasks. Generally, it clones the git repo for personal orka server, does the necessary configurations to postgresql, nginx, celery, rabbitmq, uwsgi and django and starts/restarts/updates the personal orka server.    
|  templates  |  It includes files with variables, which offers dynamic content. These files are transferred, with the appropriate additions, to the remote or local machine where commands from the ansible playbooks are executed

In case of *commons* role there is a subfolder whose description is available below:

|    File     | Description
|------------ |:---
|    tasks/main.yml    | Installs sudo and fixes missing locale for every host.

