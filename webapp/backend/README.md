Hadoop Cluster Creation Codepaths
=================================

Business logic is layered across 3 levels or domains:

Level 0 (systems) 
------------------
This level is realized with ansible playbooks.
- Handles tasks at the VM systems level (VM OS configuration, networks etc)
 - **e-science/webapp/backend/ansible** folder holds the ansible playbooks related to Hadoop Cluster creation and management for personal orka server.
 - **e-science/deploy/ansible** folder holds the ansible playbooks related to orka_portal server deployment.

Level 1 (orka-domain logic) 
---------------------------
This level is realized with python code.
- Wrappers for ~okeanos api, openssh for remote execution of hadoop mini-shell commands, bash shell and ansible scripts from Level 0
- Handles communication with clients (calls to application endpoints coming through django_rest_framework)

Level 2 (async tasks) -> Celery App
---------------------
- Adds long running and asynchronous/parallel tasks from Level 1 to a task queue.

The stack is driven by user interaction through REST calls coming from the browser (orka-GUI) or orka-CLI.


Example Code path for Hadoop Cluster Creation
=============================================

Root project folder is **e-science**  
Backend code is in **e-science/webapp/backend**  
Frontend code in **e-science/webapp/frontend**  

Only the final leaf is noted in the following to preserve the distinction and improve readability (for example **backend/models.py** refers to the **e-science/webapp/backend.models.py** full path).
Click the :book: (browse source) icon to navigate to the relevant source code. Middle-click or right-click > open in a new tab to stay on this document.

Regarding the codeflow for a Hadoop Cluster creation, the steps are the following: 

- User initiates a **PUT** call to the **/api/clusterchoices** endpoint either through the browser (orka-GUI uses the ember framework and ultimately ajax calls) or command-line interface (orka-CLI uses the python requests module)
REST Endpoint is registered in **backend/urls.py** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/urls.py#L28-L28).
- Payload is serialized according to metadata structure defined in **backend/models.py:ClusterCreationParams** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/models.py#L56-L56) using **backend/serializers.py:ClusterCreationParamsSerializer** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/serializers.py#L111-L111) and handed off to **backend/views.py:StatusView** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/views.py#L213-L213).
- The corresponding **put** method in **backend/views.py:StatusView** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/views.py#L237-237) gets the user options calls synchronous methods and prepares parameters as necessary to hand off to Celery task manager for long-running or asynchronous tasks.
- The Celery task defined in **backend/tasks.py:create_cluster_async** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/tasks.py#L17-L17) is queued for execution as resources allow.
GET calls to the **/api/jobs** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/views.py#L183-L183) endpoint can be used for task status updates (optional) 
- The celery task method **backend/tasks.py:create_cluster_async** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/tasks.py#L17-L17) then instantiates **backend/create_cluster.py:YarnCluster** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/create_cluster.py#L36-L36) and calls **create_yarn_cluster()** [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/create_cluster.py#L476-L476) which branches off to all the ~orka domain business logic for YARN cluster creation.
YARN Cluster is created as a two step process: (i) create the bare cluster [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/create_cluster.py#L425-L425) as a group of connected ~okeanos VMs (ii) initialize Hadoop core services [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/run_ansible_playbooks.py#L30-L30) as well as any Ecosystem services and configuration included in the selected template.  
Code flow runs through: 
 - authentication [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/okeanos_utils.py#L932-L932)
 - project resource checks [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/okeanos_utils.py#L978-L978)
 - user resource checks [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/create_cluster.py#L92-L214)
 - ~okeanos infrastructure cluster creation commands using  [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/okeanos_utils.py#L1271-L1271)
 - updating application state to DB for cluster creation [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/django_db_after_login.py#L102-102)
 - cluster and Hadoop initialization using ansible playbooks [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/run_ansible_playbooks.py#L30-L30)
 - updating application state to DB for Hadoop initialization [:book:](https://github.com/grnet/e-science/blob/0.3.0/webapp/backend/django_db_after_login.py#L207-207)
