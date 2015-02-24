#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script installs and configures a Hadoop-Yarn cluster using Ansible.

@author: Ioannis Stenos, Nick Vrionis
"""
import os
from os.path import dirname, abspath, isfile
import logging
from backend.models import ClusterInfo
from django_db_after_login import db_hadoop_update
from celery import current_task
from cluster_errors_constants import HADOOP_STATUS_ACTIONS, REVERSE_HADOOP_STATUS
from okeanos_utils import set_cluster_state

# Definitions of return value errors
from cluster_errors_constants import error_ansible_playbook, REPORT, SUMMARY
# Ansible constants
playbook = 'site.yml'
ansible_playbook = dirname(abspath(__file__)) + '/ansible/' + playbook
ansible_hosts_prefix = 'ansible_hosts_'
ansible_verbosity = ' -vvvv'



def install_yarn(token, hosts_list, master_ip, cluster_name, hadoop_image, ssh_file):
    """
    Calls ansible playbook for the installation of yarn and all
    required dependencies. Also  formats and starts yarn.
    """
    list_of_hosts = hosts_list
    master_hostname = list_of_hosts[0]['fqdn'].split('.', 1)[0]
    hostname_master = master_ip
    cluster_size = len(list_of_hosts)
    cluster_id = cluster_name.rsplit('-',1)[1]
    # Create ansible_hosts file
    try:
        hosts_filename = create_ansible_hosts(cluster_name, list_of_hosts,
                                         hostname_master)
        # Run Ansible playbook
        ansible_create_cluster(hosts_filename, cluster_size, hadoop_image, ssh_file)
        # Format and start Hadoop cluster
        set_cluster_state(token, cluster_id,
                          ' Yarn Cluster is active', status='Active',
                          master_IP=master_ip)
        ansible_manage_cluster(cluster_id, 'format')
        ansible_manage_cluster(cluster_id, 'start')
    except Exception, e:
        msg = 'Error while running Ansible '
        raise RuntimeError(msg, error_ansible_playbook)
    finally:
        os.system('rm /tmp/master_' + master_hostname + '_pub_key ')
    logging.log(SUMMARY, ' Yarn Cluster is active. You can access it through '
                + hostname_master + ':8088/cluster')


def create_ansible_hosts(cluster_name, list_of_hosts, hostname_master):
    """
    Function that creates the ansible_hosts file and
    returns the name of the file.
    """

    # Turns spaces to underscores from cluster name postfixed with cluster id
    # and appends it to ansible_hosts. The ansible_hosts file will now have a
    # unique name

    hosts_filename = os.getcwd() + '/' + ansible_hosts_prefix + cluster_name.replace(" ", "_")
    # Create ansible_hosts file and write all information that is
    # required from Ansible playbook.
    with open(hosts_filename, 'w+') as target:
        target.write('[master]' + '\n')
        target.write(list_of_hosts[0]['fqdn'])
        target.write(' private_ip='+list_of_hosts[0]['private_ip'])
        target.write(' ansible_ssh_host=' + hostname_master + '\n' + '\n')
        target.write('[slaves]'+'\n')

        for host in list_of_hosts[1:]:
            target.write(host['fqdn'])
            target.write(' private_ip='+host['private_ip'])
            target.write(' ansible_ssh_port='+str(host['port']))
            target.write(' ansible_ssh_host='+ hostname_master +'\n')
    return hosts_filename


def ansible_manage_cluster(cluster_id, action):
    """
    Start,stop or format a hadoop cluster, depending on the action arg.
    Updates database only when starting or stopping a cluster.
    """
    cluster = ClusterInfo.objects.get(id=cluster_id)
    current_hadoop_status = REVERSE_HADOOP_STATUS[cluster.hadoop_status]
    cluster_name_postfix_id = '%s%s%s' % (cluster.cluster_name, '-', cluster_id)
    hosts_filename = os.getcwd() + '/' + ansible_hosts_prefix + cluster_name_postfix_id.replace(" ", "_")
    if isfile(hosts_filename):
        state = ' %s %s cluster' %(HADOOP_STATUS_ACTIONS[action][1], cluster.cluster_name)
        db_hadoop_update(cluster_id, 'Pending', state)
        ansible_code = 'ansible-playbook -i ' + hosts_filename + ' ' + ansible_playbook + ansible_verbosity + ' -e "choose_role=yarn start_yarn=True" -t ' + action
        ansible_exit_status = execute_ansible_playbook(ansible_code)

        if ansible_exit_status == 0:
            msg = ' Cluster %s %s' %(cluster.cluster_name, HADOOP_STATUS_ACTIONS[action][2])
            db_hadoop_update(cluster_id, current_hadoop_status, msg)
            return msg

        db_hadoop_update(cluster_id, current_hadoop_status, 'Error in Hadoop action')

    else:
        msg = ' Ansible hosts file [%s] does not exist' % hosts_filename
        raise RuntimeError(msg)


def ansible_create_cluster(hosts_filename, cluster_size, hadoop_image, ssh_file):
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
    level = logging.getLogger().getEffectiveLevel()

    # Create debug file for ansible
    debug_file_name = "create_cluster_debug_" + hosts_filename.split(ansible_hosts_prefix, 1)[1] + ".log"
    ansible_log = " >> " + os.path.join(os.getcwd(), debug_file_name)
    # find ansible playbook (site.yml)


    # Create command that executes ansible playbook
    ansible_code = 'ansible-playbook -i ' + hosts_filename + ' ' + ansible_playbook + ansible_verbosity + ' -f ' + str(cluster_size) + ' -e "choose_role=yarn ssh_file_name=' + ssh_file

    # hadoop_image flag(true/false)
    if hadoop_image:
        # true -> use an available image (hadoop pre-installed)
        ansible_code += '" -t postconfig' + ansible_log
    else:
        # false -> use a bare VM
        ansible_code += '"' + ansible_log
    # Execute ansible
    execute_ansible_playbook(ansible_code)


def execute_ansible_playbook(ansible_command):
    """
    Executes ansible command given as argument
    """
    exit_status = os.system(ansible_command)
    if exit_status != 0:
        msg = ' Ansible failed with exit status %d' % exit_status
        raise RuntimeError(msg, exit_status)

    return 0
