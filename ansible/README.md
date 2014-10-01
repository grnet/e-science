How to run the Ansible playbook
---

This Ansible playbook has three distinct roles:
 - hadoop. Installs and configures hadoop-1.2.1 on ~okeanos cluster. 
 - webserver. Installs Django, PostgreSql and celery on a okeanos virtual machine.
 - yarn. Installs and configures hadoop-2.5.1 yarn on ~okeanos cluster.

and one common for all hosts:
 - commons. Updates, installs sudo and fixes missing locale for every host.
