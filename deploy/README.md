# Deploy Orka Server
A collection of python and ansible scripts have been assembled in `<project_root>/deploy` to facilitate the deployment of a specific version of the application.  
The environment consists of a standalone Virtual Machine running a release configuration with the Nginx-uWSGI-Postgres stack, serving the application from a public IP.
For more information check the e-science/orka/README.md file.

## Ansible playbook

This ansible playbook is called by the `deploy_orka_server.py` python script. Depending on the action executed by the python script, ansible will perform different tasks. The actions of `deploy_orka_server.py` and their corresponding ansible tasks are:

- creation of an ~okeanos Personal Orka Server image. For this action, ansible installs the software packages required for the image to function later as a personal orka server.
- starting a personal orka server. For this action, ansible starts all personal orka server processes, after doing the required configurations.
- restarting the personal orka server. For this action, ansible restarts the personal orka server processes.
- updating the personal orka server. For this action, ansible updates the project git directories from remote grnet/e-science git repository and restarts the server.

The table below describes the ansible files and folders:

|    File     | Description
|:------------ |:---
|  group_vars/webserver.yml |  Constants and default values for variables used by webserver playbook.
|  roles      |  Ansible roles: webserver and commons and their corresponding subfolders.
|  staging.yml   |  Entry point of ansible webserver playbook and distributes the ansible tasks based on the input arguments.
|  setup_orka_admin.yml    | Called when `deploy_orka_server.py` is used with argument create. Installs on an empty ~okeanos VM all the software packages needed for personal orka server to function.
|  deploy_sample_file.yml    | Example file, used as a template for the user-created YAML file that contains the mandatory passwords needed for the personal orka server to start.
|  deploy_orka_server.py | Python script that calls the ansible webserver playbook. 
|  ansible.cfg     | Ansible configuration file.


 In the case of *webserver* role, there are three subfolders, with the following description:

|    File     | Description
|:------------ |:---
|    files    |  Includes the necessary files for executing specific services. They are transferred unchanged to the remote or local machine where commands from the ansible playbooks are executed
|    tasks/main.yml    |  Called from `deploy_orka_server.py` script for various tasks. Generally, it clones the git repo for personal orka server, does the necessary configurations to postgresql, nginx, celery, rabbitmq, uwsgi and django and starts/restarts/updates the personal orka server.    
|  templates  |  Includes files with variables, which offers dynamic content. These files are transferred, with the appropriate additions, to the remote or local machine where commands from the ansible playbooks are executed

In case of *commons* role there is a subfolder with one file:

|    File     | Description
|:------------ |:---
|    tasks/main.yml    | Installs sudo and fixes missing locale for every host.

