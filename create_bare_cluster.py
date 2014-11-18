#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script creates a bare cluster on ~okeanos.

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
from okeanos_utils import *
from kamaki.clients.cyclades import CycladesClient

# Definitions of return value errors
error_syntax_clustersize = -1
error_syntax_cpu_master = -2
error_syntax_ram_master = -3
error_syntax_disk_master = -4
error_syntax_cpu_slave = -5
error_syntax_ram_slave = -6
error_syntax_disk_slave = -7
error_syntax_logging_level = -8
error_syntax_disk_template = -9
error_quotas_cyclades_disk = -10
error_quotas_cpu = -11
error_quotas_ram = -12
error_quotas_clustersize = -13
error_flavor_id = -15
error_user_quota = -22
error_flavor_list = -23
error_syntax_auth_token = -32

# Global constants
REPORT = 25  # Define logging level of REPORT
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes


def get_flavor_ids(cpu, ram, disk, disk_template, cycladesclient):
    '''Return the flavor id based on cpu,ram,disk_size and disk template'''
    try:
        flavor_list = cycladesclient.list_flavors(True)
    except Exception:
        logging.exception('Could not get list of flavors')
        sys.exit(error_flavor_list)
    flavor_id = 0
    for flavor in flavor_list:
        if flavor['ram'] == ram and \
            flavor['SNF:disk_template'] == disk_template and \
                flavor['vcpus'] == cpu and \
                flavor['disk'] == disk:
            flavor_id = flavor['id']

    return flavor_id
    
def check_quotas(auth, req_quotas):
    '''
    Checks if user quota are enough for what he needed to create the cluster.
    If limit minus (used and pending) are lower or
    higher than what user requests.Also divides with 1024*1024*1024
    to transform bytes to gigabytes.
     '''
    try:
        dict_quotas = auth.get_quotas()
    except Exception:
        logging.exception('Could not get user quota')
        sys.exit(error_user_quota)
    # Get project id for Synnefo v0.16
    project_id = get_project_id() 
    limit_cd = dict_quotas[project_id]['cyclades.disk']['limit']
    usage_cd = dict_quotas[project_id]['cyclades.disk']['usage']
    pending_cd = dict_quotas[project_id]['cyclades.disk']['pending']
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd) / Bytes_to_GB
    if available_cyclades_disk_GB < req_quotas['cyclades_disk']:
        logging.error('Cyclades disk out of limit')
        sys.exit(error_quotas_cyclades_disk)

    limit_cpu = dict_quotas[project_id]['cyclades.cpu']['limit']
    usage_cpu = dict_quotas[project_id]['cyclades.cpu']['usage']
    pending_cpu = dict_quotas[project_id]['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu
    if available_cpu < req_quotas['cpu']:
        logging.error('Cyclades cpu out of limit')
        sys.exit(error_quotas_cpu)

    limit_ram = dict_quotas[project_id]['cyclades.ram']['limit']
    usage_ram = dict_quotas[project_id]['cyclades.ram']['usage']
    pending_ram = dict_quotas[project_id]['cyclades.ram']['pending']
    available_ram = (limit_ram-usage_ram-pending_ram) / Bytes_to_MB
    if available_ram < req_quotas['ram']:
        logging.error('Cyclades ram out of limit')
        sys.exit(error_quotas_ram)
    limit_vm = dict_quotas[project_id]['cyclades.vm']['limit']
    usage_vm = dict_quotas[project_id]['cyclades.vm']['usage']
    pending_vm = dict_quotas[project_id]['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm
    if available_vm < req_quotas['vms']:
        logging.error('Cyclades vms out of limit')
        sys.exit(error_quotas_clustersize)
    logging.log(REPORT, ' Cyclades Cpu,Disk and Ram quotas are ok.')
    return


def create_cluster(name, clustersize, cpu_master, ram_master, disk_master,
                   disk_template, cpu_slave, ram_slave, disk_slave, token,
                   image, auth_url='https://accounts.okeanos.grnet.gr'
                   '/identity/v2.0'):
    '''
    This function of our script takes the arguments given and calls the
    check_quota function. Also, calls get_flavor_id to find the matching
    flavor_ids from the arguments given and finds the image id of the
    image given as argument. Then instantiates the Cluster and creates
    the virtual machine cluster of one master and clustersize-1 slaves.
    Calls the function to install hadoop to the cluster.
    '''
    logging.log(REPORT, ' 1.Credentials  and  Endpoints')
    # Finds user public ssh key
    USER_HOME = os.path.expanduser('~')
    global cluster_size
    cluster_size = clustersize
    pub_keys_path = os.path.join(USER_HOME, ".ssh/id_rsa.pub")
    auth = check_credentials(token, auth_url)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    flavor_master = get_flavor_ids(cpu_master, ram_master,
                                  disk_master, disk_template,
                                  cyclades)
    flavor_slaves = get_flavor_ids(cpu_slave, ram_slave,
                                  disk_slave, disk_template,
                                  cyclades)
    if flavor_master == 0 or flavor_slaves == 0:
        logging.error('Combination of cpu, ram, disk and disk_template do'
                      ' not match an existing id')

        sys.exit(error_flavor_id)
    # Total cpu,ram and disk needed for cluster
    cpu = cpu_master + (cpu_slave)*(clustersize-1)
    ram = ram_master + (ram_slave)*(clustersize-1)
    cyclades_disk = disk_master + (disk_slave)*(clustersize-1)
    # The resources requested by user in a dictionary
    req_quotas = {'cpu': cpu, 'ram': ram, 'cyclades_disk': cyclades_disk,
                  'vms': clustersize}
    check_quotas(auth, req_quotas)
    plankton = init_plankton(endpoints['plankton'], token)
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the arg given
    for lst in list_current_images:
        if lst['name'] == image:
            chosen_image = lst

    logging.log(REPORT, ' 2.Create  virtual  cluster')
    cluster = Cluster(cyclades,
                      prefix=name,
                      flavor_id_master=flavor_master,
                      flavor_id_slave=flavor_slaves,
                      image_id=chosen_image['id'],
                      size=clustersize,
                      net_client=init_cyclades_netclient(endpoints['network'],
                                                         token),
                      auth_cl=auth)

    HOSTNAME_MASTER , server = cluster.create('', pub_keys_path,'')
    sleep(15)
    #wait for the machines to be pingable
    logging.log(REPORT, ' Bare cluster has been created.')	
    # Return master node ip and server dict
    return HOSTNAME_MASTER , server 


def main(opts):
    '''
    The main function calls create_cluster with the arguments given from
    command line.
    '''
    create_cluster(opts.name, opts.clustersize, opts.cpu_master,
                   opts.ram_master, opts.disk_master, opts.disk_template,
                   opts.cpu_slave, opts.ram_slave, opts.disk_slave,
                   opts.token, opts.image, opts.auth_url)

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

            
