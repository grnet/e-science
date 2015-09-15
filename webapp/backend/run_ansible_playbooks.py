#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script installs and configures a Hadoop-Yarn cluster using Ansible.

@author: Ioannis Stenos, Nick Vrionis
"""
import os
from os.path import dirname, abspath, isfile
import logging
import subprocess
from backend.models import ClusterInfo, UserInfo
from django_db_after_login import db_hadoop_update
from celery import current_task
from cluster_errors_constants import HADOOP_STATUS_ACTIONS, REVERSE_HADOOP_STATUS, REPORT, SUMMARY, \
    error_ansible_playbook, const_hadoop_status_started, hadoop_images_ansible_tags, pithos_images_uuids_properties, unmask_token, encrypt_key
from backend.models import OrkaImage
from ansible import errors

# Definitions of return value errors
# Ansible constants
playbook = 'site.yml'
ansible_playbook = dirname(abspath(__file__)) + '/ansible/' + playbook
ansible_hosts_prefix = 'ansible_hosts_'
ansible_verbosity = ' -v'


def install_yarn(*args):
    """
    Calls ansible playbook for the installation of yarn and all
    required dependencies. Also  formats and starts yarn or cloudera hadoop distribution.
    Takes positional arguments as args tuple.
    args: token, hosts_list, master_ip, cluster_name, orka_image_uuid, ssh_file, replication_factor, dfs_blocksize
    """
    from okeanos_utils import set_cluster_state
    list_of_hosts = args[1]
    master_hostname = list_of_hosts[0]['fqdn'].split('.', 1)[0]
    cluster_size = len(list_of_hosts)
    cluster_id = args[3].rsplit('-', 1)[1]
    # Create ansible_hosts file
    try:
        hosts_filename = create_ansible_hosts(args[3], list_of_hosts, args[2])
        # Run Ansible playbook
        ansible_create_cluster(hosts_filename, cluster_size, args[4], args[5], args[0], args[6], args[7], args[8])
        # Format and start Hadoop cluster
        set_cluster_state(args[0], cluster_id,
                          'Yarn Cluster is active', status='Active',
                          master_IP=args[2])
        ansible_manage_cluster(cluster_id, 'format')
        ansible_manage_cluster(cluster_id, 'start')

    except Exception, e:
        msg = 'Error while running Ansible %s' % e
        raise RuntimeError(msg, error_ansible_playbook)
    finally:
        subprocess.call('rm /tmp/master_' + master_hostname + '_pub_key_* ', shell=True)
    logging.log(SUMMARY, 'Yarn Cluster is active. You can access it through '
                + args[2] + ':8088/cluster')


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
    master_host = '[master]'
    slaves_host = '[slaves]'
    cluster_id = cluster_name.rsplit('-',1)[1]
    cluster = ClusterInfo.objects.get(id=cluster_id)
    if 'cdh' in cluster.os_image.lower():
        master_host = '[master_cloud]'
        slaves_host = '[slaves_cloud]'

    with open(hosts_filename, 'w+') as target:
        target.write(master_host + '\n')
        target.write(list_of_hosts[0]['fqdn'])
        target.write(' private_ip='+list_of_hosts[0]['private_ip'])
        target.write(' ansible_ssh_host=' + hostname_master + '\n' + '\n')
        target.write(slaves_host +'\n')

        for host in list_of_hosts[1:]:
            target.write(host['fqdn'])
            target.write(' private_ip='+host['private_ip'])
            target.write(' ansible_ssh_port='+str(host['port']))
            target.write(' ansible_ssh_host='+ hostname_master +'\n')
    return hosts_filename


def modify_ansible_hosts_file(cluster_name, list_of_hosts='', master_ip='', action='', slave_hostname=''):
    """
    Function that modifies the ansible_hosts file with
    the scaled cluster slave hostnames, adding the new slaves,
    deleting the removed slaves or joining in one entry all the slaves.
    """
    hosts_filename = os.getcwd() + '/' + ansible_hosts_prefix + cluster_name.replace(" ", "_")
    # Create ansible_hosts file and write all information that is
    # required from Ansible playbook.
    if action == 'add_slaves':
        new_slaves_host = '[new_slaves]'
        with open(hosts_filename, 'a+') as target:
            target.write(new_slaves_host + '\n')
            for host in list_of_hosts:
                target.write('{0} private_ip={1} ansible_ssh_port={2} ansible_ssh_host={3}\n'.format(host['fqdn'],
                                                                                                host['private_ip'],
                                                                                              str(host['port']), master_ip))    
    elif action == 'remove_slaves':
        remove_slaves_command = "sed -i.bak '/{0}/d' {1}".format(slave_hostname, hosts_filename)
        subprocess.call(remove_slaves_command, shell=True)
    elif action == 'join_slaves':
        join_slaves_command = "sed -i.bak '/\[new\_slaves\]/d' {0}".format(hosts_filename)
        subprocess.call(join_slaves_command, shell=True)
        
    return hosts_filename


def map_command_to_ansible_actions(action, image, pre_action_status):
    """
    Function to map the start,stop or format commands to the correct ansible actions in
    correct sequence, depending also on the image used. Returns a list of the Ansible
    tags that will run.
    """
    ansible_tags = hadoop_images_ansible_tags[image]
    # format request for started cluster > stop [> clean ]> format > start
    # if stopped cluster, then only format
    if action == "format" and pre_action_status == const_hadoop_status_started:
        return ['stop', 'CLOUDstop', action, 'start', 'CLOUDstart'] if 'cloudera' in image else \
            [ansible_tags['stop'], action, ansible_tags['start']]

    elif action == "format" and pre_action_status != const_hadoop_status_started:
        return ['format']

    else:
        return [action, 'CLOUD{0}'.format(action)] if 'cloudera' in image else [ansible_tags[action]]


def ansible_manage_cluster(cluster_id, action):
    """
    Perform an action on a Hadoop cluster depending on the action arg.
    Updates database only when starting or stopping a cluster.
    """
    cluster = ClusterInfo.objects.get(id=cluster_id)
    pre_action_status = cluster.hadoop_status
    if action == 'format':
        current_hadoop_status = REVERSE_HADOOP_STATUS[cluster.hadoop_status]
    else:
        current_hadoop_status = action
    orka_image = OrkaImage.objects.get(image_name=cluster.os_image)
    chosen_image = pithos_images_uuids_properties[orka_image.image_pithos_uuid]
    role = chosen_image['role']
    ANSIBLE_SEQUENCE = map_command_to_ansible_actions(action, chosen_image['image'], pre_action_status)

    cluster_name_postfix_id = '%s%s%s' % (cluster.cluster_name, '-', cluster_id)
    hosts_filename = os.getcwd() + '/' + ansible_hosts_prefix + cluster_name_postfix_id.replace(" ", "_")
    if isfile(hosts_filename):
        state = '%s %s' %(HADOOP_STATUS_ACTIONS[action][1], cluster.cluster_name)
        current_task.update_state(state=state)
        db_hadoop_update(cluster_id, 'Pending', state)
        debug_file_name = "create_cluster_debug_" + hosts_filename.split(ansible_hosts_prefix, 1)[1] + ".log"
        ansible_log = " >> " + os.path.join(os.getcwd(), debug_file_name)
        ansible_code_generic = 'ansible-playbook -i {0} {1} {2} -e "choose_role={3} manage_cluster={3}" -t'.format(hosts_filename, ansible_playbook, ansible_verbosity, role)

        for hadoop_action in ANSIBLE_SEQUENCE:
            ansible_code = '{0} {1} {2}'.format(ansible_code_generic, hadoop_action, ansible_log)
            try:
                execute_ansible_playbook(ansible_code)
            except Exception, e:
                msg = str(e.args[0])
                db_hadoop_update(cluster_id, 'undefined', msg)
                raise RuntimeError(msg)

        msg = 'Cluster %s %s' %(cluster.cluster_name, HADOOP_STATUS_ACTIONS[action][2])
        db_hadoop_update(cluster_id, current_hadoop_status, msg)
        return msg


    else:
        msg = 'Ansible hosts file [%s] does not exist' % hosts_filename
        raise RuntimeError(msg)


def ansible_create_cluster(hosts_filename, cluster_size, orka_image_uuid, ssh_file, token, replication_factor,
                           dfs_blocksize, admin_password):
    """
    Calls the ansible playbook that installs and configures
    hadoop and everything needed for hadoop to be functional.
    hosts_filename is the name of ansible_hosts file.
    If a specific hadoop image was used in the VMs creation, ansible
    playbook will not install Hadoop-Yarn and will only perform
    the appropriate configuration.
    """
    logging.log(REPORT, ' Ansible starts Yarn installation on master and '
                        'slave nodes')
    level = logging.getLogger().getEffectiveLevel()
    # chosen image includes role and tags properties
    chosen_image = pithos_images_uuids_properties[orka_image_uuid]
    # Create debug file for ansible
    debug_file_name = "create_cluster_debug_" + hosts_filename.split(ansible_hosts_prefix, 1)[1] + ".log"
    ansible_log = " >> " + os.path.join(os.getcwd(), debug_file_name)
    # find ansible playbook (site.yml)
    uuid = UserInfo.objects.get(okeanos_token=token).uuid
    # Create command that executes ansible playbook
    ansible_code = 'ansible-playbook -i {0} {1} {2} '.format(hosts_filename, ansible_playbook, ansible_verbosity) + \
    '-f {0} -e "choose_role={1} ssh_file_name={2} token={3} '.format(str(cluster_size), chosen_image['role'], ssh_file, unmask_token(encrypt_key, token)) + \
    'dfs_blocksize={0}m dfs_replication={1} uuid={2} admin_password={3}" {4}'.format(dfs_blocksize, replication_factor, uuid, admin_password, chosen_image['tags'])

    # Execute ansible
    ansible_code += ansible_log
    execute_ansible_playbook(ansible_code)


def ansible_scale_cluster(hosts_filename, new_slaves_size=1, orka_image_uuid='', user_id='',action='add_slaves', slave_hostname=''):
    """
    Calls the  ansible playbook that configures the added nodes 
    in a scaled hadoop cluster or decommissions the node to be removed.
    """
    if action == 'add_slaves':
        chosen_image = pithos_images_uuids_properties[orka_image_uuid]
        list_of_ansible_tags = chosen_image['tags'].split(',')
        scale_cluster_tags = ['{0}scale'.format(t) for t in list_of_ansible_tags]
        tags = ",".join(scale_cluster_tags)       
    else:
        tags = '-t remove_yarn_nodes'
    # Create debug file for ansible
    debug_file_name = "create_cluster_debug_" + hosts_filename.split(ansible_hosts_prefix, 1)[1] + ".log"
    ansible_log = " >> " + os.path.join(os.getcwd(), debug_file_name)
    
    # -t postconfigscale
    ansible_code = 'ansible-playbook -i {0} {1} {2} '.format(hosts_filename, ansible_playbook, ansible_verbosity) + \
    '-f {0} -e "manage_cluster={1} hostname={2} uuid={3}" {4}'.format(str(new_slaves_size), action, slave_hostname, user_id, tags)
    # Execute ansible
    ansible_code += ansible_log
    try:
        execute_ansible_playbook(ansible_code)
    except Exception, e:
        msg = str(e.args[0])
        raise RuntimeError(msg)


def execute_ansible_playbook(ansible_command):
    """
    Executes ansible command given as argument
    """
    try:
        exit_status = subprocess.call(ansible_command, shell=True)
        if exit_status > 0:
            msg = 'Ansible failed with exit status %d' % exit_status
            raise RuntimeError(msg, exit_status)
    except OSError as e:
        msg = 'Ansible command execution failed %s' % e
        raise RuntimeError(msg, e)

    return 0
