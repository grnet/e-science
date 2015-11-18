# Ansible playbooks

Below are available in tables, the ansible files and folders with their corresponding description:

|    File     | Description
|------------ |:---
|  group_vars |  It includes constants used by ansible playbooks
|  roles      |  It includes the Ansible roles: yarn, cloudera, commons
|  site.yml   |  It is the entry point of Ansible and shares the Ansible tasks
|  rollback_scale_cluster    | It is called when the cluster scaling fails, so as to rollback the procedure
|  scale_cluster_add_node    | It is called in order to add a node to the Hadoop cluster
|  scale_cluster_remove_node | It is called in order to remove a node from the Hadoop cluster
|  start_cloudera | It is called so as to start or stop the cloudera services
|  start_yarn     | It is called so as to start or stop the yarn or/and ecosystem services

Every Ansible role is in a separate subfolder. In the cases of *yarn* and *cloudera* roles, there are three subfolders, whose description is common and is available below:

|    File     | Description
|------------ |:---
|    files    |  It includes the files that are necessary for the execution of specific services. They are transferred unchanged to the remote machine where commands from the ansible playbooks are executed
|    tasks    |  In case of yarn it installs and configures apache hadoop distribution on the cluster. In case of cloudera it installs and configures, from the cloudera repositories, the cloudera distribution on the cluster
|  templates  |  It includes files with variables, which offers dynamic content. These files are transferred, with the appropriate additions, to the remote machine where commands from the ansible playbooks are executed

In case of *commons* role there is a subfolder whose description is available below:

|    File     | Description
|------------ |:---
|    tasks    | Installs sudo and fixes missing locale for every host.