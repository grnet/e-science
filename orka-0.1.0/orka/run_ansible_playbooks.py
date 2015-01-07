#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script creates a virtual cluster on ~okeanos and installs Hadoop-Yarn
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
"""

from sys import exit, argv
import os
from os.path import dirname, abspath, join
import logging
from optparse import OptionParser
from reroute_ssh import reroute_ssh_prep

# Definitions of return value errors
from cluster_errors_constants import error_ansible_playbook, REPORT, SUMMARY


def install_yarn(hosts_list, master_ip, cluster_name, hadoop_image):
    """
    Calls ansible playbook for the installation of yarn and all
    required dependencies. Also  formats and starts yarn.
    """
    list_of_hosts = hosts_list
    master_hostname = list_of_hosts[0]['fqdn'].split('.', 1)[0]
    HOSTNAME_MASTER = master_ip
    cluster_size = len(list_of_hosts)
    # Create ansible_hosts file
    try:
        file_name = create_ansible_hosts(cluster_name, list_of_hosts,
                                         HOSTNAME_MASTER)
    except Exception:
        msg = 'Error while creating ansible hosts file'
        raise RuntimeError(msg, error_ansible_playbook)
    # Run Ansible playbook
    run_ansible(file_name, cluster_size, hadoop_image)
    logging.log(SUMMARY, ' Yarn Cluster is active. You can access it through '
                + HOSTNAME_MASTER + ':8088/cluster')
    os.system('rm /tmp/master_' + master_hostname + '_pub_key')


def create_ansible_hosts(cluster_name, list_of_hosts, HOSTNAME_MASTER):
    """
    Function that creates the ansible_hosts file and
    returns the name of the file.
    """
    ansible_hosts_prefix = cluster_name.replace(" ", "")
    ansible_hosts_prefix = ansible_hosts_prefix.replace(":", "")

    # Removes spaces and ':' from cluster name and appends it to ansible_hosts
    # The ansible_hosts file will now have a timestamped name

    filename = os.getcwd() + '/ansible_hosts_' + ansible_hosts_prefix
    # Create ansible_hosts file and write all information that is
    # required from Ansible playbook.
    with open(filename, 'w+') as target:
        target.write('[master]' + '\n')
        target.write(list_of_hosts[0]['fqdn'])
        target.write(' private_ip='+list_of_hosts[0]['private_ip'])
        target.write(' ansible_ssh_host=' + HOSTNAME_MASTER + '\n' + '\n')
        target.write('[slaves]'+'\n')

        for host in list_of_hosts[1:]:
            target.write(host['fqdn'])
            target.write(' private_ip='+host['private_ip'])
            target.write(' ansible_ssh_port='+str(host['port']))
            target.write(' ansible_ssh_host='+list_of_hosts[0]['fqdn'] + '\n')
    return filename


def run_ansible(filename, cluster_size, hadoop_image):
    """
    Calls the ansible playbook that installs and configures
    hadoop and everything needed for hadoop to be functional.
    Filename as argument is the name of ansible_hosts file.
    """
    logging.log(REPORT, ' Ansible starts Yarn installation on master and '
                        'slave nodes')
    # First time call of Ansible playbook install.yml executes tasks
    # required for hadoop installation on every virtual machine. Runs with
    # -f flag which is the fork argument of Ansible.
    level = logging.getLogger().getEffectiveLevel()
    # ansible_log file to write if logging level is
    # different than report or summary
    ansible_log = " > ansible.log"
    if level == REPORT or level == SUMMARY:
        ansible_log = ""
    BASE_DIR = dirname(abspath(__file__))
    ANSIBLE_PLAYBOOK_PATH = BASE_DIR + '/ansible/site.yml'

    if hadoop_image:
        exit_status = os.system('export ANSIBLE_HOST_KEY_CHECKING=False;'
                            'ansible-playbook -i ' + filename + ' ' +
                            ANSIBLE_PLAYBOOK_PATH +
                            ' -f ' + str(cluster_size) +
                            ' -e "choose_role=yarn format=True start_yarn=True" -t postconfig'
                            + ansible_log)
    else:
        exit_status = os.system('export ANSIBLE_HOST_KEY_CHECKING=False;'
                                'ansible-playbook -i ' + filename + ' ' +
                                ANSIBLE_PLAYBOOK_PATH +
                                ' -f ' + str(cluster_size) +
                                ' -e "choose_role=yarn format=True start_yarn=True"'
                                + ansible_log)
    if exit_status != 0:
        msg = ' Ansible failed with exit status %d' % exit_status
        raise RuntimeError(msg, exit_status)


def main(opts):
    """
    The main function calls reroute_ssh_prep with the arguments given from
    command line.
    """
    reroute_ssh_prep(opts.hosts_list, opts.master_ip, opts.cluster_name)


if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--server',
                      action='store', type='string', dest='server',
                      metavar="SERVER",
                      help='a list with information about the cluster(names and fqdn of the nodes)')
    parser.add_option('--public_ip',
                      action='store', type='string', dest='public_ip',
                      metavar="PUBLIC_IP",
                      help='it is the ipv4 of the master node ')
    parser.add_option('--cluster_name',
                      action='store', type='string', dest='cluster_name',
                      metavar='CLUSTER_NAME',
                      help='the name of the cluster')

    opts, args = parser.parse_args(argv[1:])

    main(opts)
