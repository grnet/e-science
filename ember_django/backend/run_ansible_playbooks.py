#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script installs and configures a Hadoop-Yarn cluster using Ansible.

@author: Ioannis Stenos, Nick Vrionis
"""
import os
from os.path import dirname, abspath
import logging

# Definitions of return value errors
from cluster_errors_constants import error_ansible_playbook, REPORT, SUMMARY
playbook = 'site.yml'

def install_yarn(hosts_list, master_ip, cluster_name, hadoop_image, ssh_file):
    """
    Calls ansible playbook for the installation of yarn and all
    required dependencies. Also  formats and starts yarn.
    """
    list_of_hosts = hosts_list
    master_hostname = list_of_hosts[0]['fqdn'].split('.', 1)[0]
    hostname_master = master_ip
    cluster_size = len(list_of_hosts)
    # Create ansible_hosts file
    try:
        hosts_filename = create_ansible_hosts(cluster_name, list_of_hosts,
                                         hostname_master)
        # Run Ansible playbook
        run_ansible(hosts_filename, cluster_size, hadoop_image, ssh_file)
    except Exception:
        msg = 'Error while running ansible'
        raise RuntimeError(msg, error_ansible_playbook)
    finally:
        os.system('rm /tmp/master_' + master_hostname + '_pub_key ' + hosts_filename)
    logging.log(SUMMARY, ' Yarn Cluster is active. You can access it through '
                + hostname_master + ':8088/cluster')


def create_ansible_hosts(cluster_name, list_of_hosts, hostname_master):
    """
    Function that creates the ansible_hosts file and
    returns the name of the file.
    """
    ansible_hosts_prefix = cluster_name.replace(" ", "_")

    # Turns spaces to underscores from cluster name and appends it to ansible_hosts
    # The ansible_hosts file will now have a timestamped name

    hosts_filename = os.getcwd() + '/ansible_hosts_' + ansible_hosts_prefix
    # Create ansible_hosts file and write all information that is
    # required from Ansible playbook.
    with open(hosts_filename, 'w+') as target:
        target.write('[master]' + '\n')
        target.write(list_of_hosts[0]['fqdn'])
        target.write(' private_ip='+list_of_hosts[0]['private_ip'])
        target.write(' ansible_ssh_pass='+list_of_hosts[0]['password'])
        target.write(' ansible_ssh_host=' + hostname_master + '\n' + '\n')
        target.write('[slaves]'+'\n')

        for host in list_of_hosts[1:]:
            target.write(host['fqdn'])
            target.write(' private_ip='+host['private_ip'])
            target.write(' ansible_ssh_pass='+host['password'])
            target.write(' ansible_ssh_port='+str(host['port']))
            target.write(' ansible_ssh_host='+ hostname_master +'\n')
    return hosts_filename


def run_ansible(hosts_filename, cluster_size, hadoop_image, ssh_file):
    """
    Calls the ansible playbook that installs and configures
    hadoop and everything needed for hadoop to be functional.
    Filename as argument is the name of ansible_hosts file.
    If a hadoop image was used in the VMs creation, ansible
    playbook will not install Hadoop-Yarn and will only perform
    the appropriate configuration.
    """
    logging.log(REPORT, ' Ansible starts Yarn installation on master and '
                        'slave nodes')
    # First time call of Ansible playbook install.yml executes tasks
    # required for hadoop installation on every virtual machine. Runs with
    # -f flag which is the fork argument of Ansible.
    level = logging.getLogger().getEffectiveLevel()
    # ansible_log file to write if logging level is
    # different than report or summary
    ansible_verbosity = ""
    ansible_log = " > ansible.log"
    if level in [REPORT, SUMMARY, logging.INFO]:
        ansible_log = ""
    elif level == logging.DEBUG:
        ansible_verbosity = " -vv"
        log_file_path = os.path.join(os.getcwd(), "create_cluster_debug.log")
        ansible_log = " >> " + log_file_path
    if level == logging.INFO:
        ansible_verbosity = " -v"

    # find ansible playbook (site.yml)
    ansible_playbook = dirname(abspath(__file__)) + '/ansible/' + playbook

    ansible_code = 'ansible-playbook -i ' + hosts_filename + ' ' + ansible_playbook + ansible_verbosity + ' -f ' + str(cluster_size) + ' -e "choose_role=yarn format=True start_yarn=True ssh_file_name=' + ssh_file

    # hadoop_image flag(true/false)
    if hadoop_image:
        # true -> use an available image (hadoop pre-installed)
        ansible_code += '" -t postconfig'
    else:
        # false -> use a bare VM
        ansible_code += '"'

    exit_status = os.system(ansible_code)
    if exit_status != 0:
        msg = ' Ansible failed with exit status %d' % exit_status
        raise RuntimeError(msg, exit_status)
