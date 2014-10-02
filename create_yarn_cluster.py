#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''

import os
import sys
import nose
import string
import logging

from sys import argv
from time import sleep
from os.path import abspath
from datetime import datetime
from optparse import OptionParser

from create_bare_cluster import*
from reroute_ssh import*
from run_ansible_playbooks import*

def main(opts):
    '''
    The main function calls create_cluster with the arguments given from
    command line.
    '''
    HOSTNAME_MASTER , server = create_cluster(opts.name, opts.clustersize, opts.cpu_master,
                   		opts.ram_master, opts.disk_master, opts.disk_template,
                   		opts.cpu_slave, opts.ram_slave, opts.disk_slave,
                   		opts.token, opts.image, opts.auth_url)
    list_of_hosts = reroute_ssh_prep(server,HOSTNAME_MASTER)
    install_yarn(list_of_hosts,HOSTNAME_MASTER, opts.name)






if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    levels = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'report': REPORT,
              'info': logging.INFO,
              'debug': logging.DEBUG}

    # Create string with all available logging levels
    string_of_levels = ''
    for level_name in levels.keys():
        string_of_levels = string_of_levels + level_name + '|'
    string_of_levels = string_of_levels[:-1]

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="CLUSTER NAME",
                      help='The prefix name of the cluster')
    parser.add_option('--clustersize',
                      action='store', type='int', dest='clustersize',
                      metavar="CLUSTER SIZE",
                      help='Number of virtual cluster nodes to create ')
    parser.add_option('--cpu_master',
                      action='store', type='int', dest='cpu_master',
                      metavar='CPU MASTER',
                      help='Number of cores for the master node')
    parser.add_option('--ram_master',
                      action='store', type='int', dest='ram_master',
                      metavar='RAM MASTER',
                      help='Size of RAM (in MB) for the master node')
    parser.add_option('--disk_master',
                      action='store', type='int', dest='disk_master',
                      metavar='DISK MASTER',
                      help='Disk size (in GB) for the master node')
    parser.add_option('--disk_template',
                      action='store', type='string', dest='disk_template',
                      metavar='DISK TEMPLATE',
                      help='Disk template (drbd, or ext_vlmc)')
    parser.add_option('--cpu_slave',
                      action='store', type='int', dest='cpu_slave',
                      metavar='CPU SLAVE',
                      help='Number of cores for the slave nodes')
    parser.add_option('--ram_slave',
                      action='store', type='int', dest='ram_slave',
                      metavar='RAM SLAVE',
                      help='Size of RAM (in MB) for the slave nodes')
    parser.add_option('--disk_slave',
                      action='store', type='int', dest='disk_slave',
                      metavar='DISK SLAVE',
                      help=' Disk size (in GB) for slave nodes')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')
    parser.add_option('--image',
                      action='store', type='string', dest='image',
                      metavar='IMAGE OS',
                      help='OS for the virtual machine cluster'
                           '.Default=Debian Base',
                      default='Debian Base')

    parser.add_option('--auth_url',
                      action='store', type='string', dest='auth_url',
                      metavar='AUTHENTICATION URL',
                      help='Synnefo authentication url'
                      '.Default=https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0',
                      default='https://accounts.okeanos.grnet.gr'
                              '/identity/v2.0')

    parser.add_option('--logging_level',
                      action='store', type='string', dest='logging_level',
                      metavar='LOGGING LEVEL',
                      help='logging level:[' +
                      string_of_levels +
                      ']. Default is report',
                      default='report')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    #  If clause to catch syntax error in logging argument
    if opts.logging_level not in levels.keys():
        logging.error('invalid syntax for logging_level')
        sys.exit(error_syntax_logging_level)

    logging_level = levels[opts.logging_level]

    if opts.logging_level == 'debug':
        log_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(log_directory, "create_cluster_debug.log")
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging_level, datefmt='%H:%M:%S')

    if opts.clustersize <= 0:
        logging.error('invalid syntax for clustersize'
                      ', clustersize must be a positive integer')
        sys.exit(error_syntax_clustersize)

    if opts.cpu_master <= 0:
        logging.error('invalid syntax for cpu_master'
                      ', cpu_master must be a positive integer')
        sys.exit(error_syntax_cpu_master)

    if opts.ram_master <= 0:
        logging.error('invalid syntax for ram_master'
                      ', ram_master must be a positive integer')
        sys.exit(error_syntax_ram_master)

    if opts.disk_master <= 0:
        logging.error('invalid syntax for disk_master'
                      ', disk_master must be a positive integer')
        sys.exit(error_syntax_disk_master)

    if opts.cpu_slave <= 0:
        logging.error('invalid syntax for cpu_slave'
                      ', cpu_slave must be a positive integer')
        sys.exit(error_syntax_cpu_slave)

    if opts.ram_slave <= 0:
        logging.error('invalid syntax for ram_slave'
                      ', ram_slave must be a positive integer')
        sys.exit(error_syntax_ram_slave)

    if opts.disk_slave <= 0:
        logging.error('invalid syntax for disk_slave'
                      ', disk_slave must be a positive integer')
        sys.exit(error_syntax_disk_slave)

    if opts.disk_template not in ['drbd', 'ext_vlmc']:
        logging.error('invalid syntax for disk_template')
        sys.exit(error_syntax_disk_template)

    if not opts.token:
        logging.error('invalid syntax for authentication token')
        sys.exit(error_syntax_auth_token)
    main(opts)

