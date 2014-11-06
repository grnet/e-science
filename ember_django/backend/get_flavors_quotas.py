#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Methods for check and return ~okeanos user quota, return ~okeanos flavor list
and update the ClusterCreationParams model.

@author: Ioannis Stenos, Nick Vrionis
'''

import django
import os
from os.path import join, dirname, abspath
import sys
import logging
sys.path.append(join(dirname(abspath(__file__)), '../..'))
sys.path.append(join(dirname(abspath(__file__)), '..'))
#import okeanos_utils
from okeanos_utils import *
from kamaki.clients.cyclades import CycladesClient
from backend.models import ClusterCreationParams


# Definitions of return value errors
error_flavor_list = -23
error_user_quota = -22
error_syntax_logging_level = -24
error_syntax_auth_token = -25


# Global constants
Mbytes_to_GB = 1024  # Global to convert megabytes to gigabytes
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'


def check_quota(token):
    '''
    Checks if user available quota .
    Available = limit minus (used and pending).Also divides with 1024*1024*1024
    to transform bytes to gigabytes.
     '''

    auth = check_credentials(token, auth_url)

    try:
        dict_quotas = auth.get_quotas()
    except Exception:
        logging.exception('Could not get user quota')
        sys.exit(error_user_quota)
    limit_cd = dict_quotas['system']['cyclades.disk']['limit'] / Bytes_to_GB
    usage_cd = dict_quotas['system']['cyclades.disk']['usage'] / Bytes_to_GB
    pending_cd = dict_quotas['system']['cyclades.disk']['pending'] / Bytes_to_GB
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd)

    limit_cpu = dict_quotas['system']['cyclades.cpu']['limit']
    usage_cpu = dict_quotas['system']['cyclades.cpu']['usage']
    pending_cpu = dict_quotas['system']['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu

    limit_ram = dict_quotas['system']['cyclades.ram']['limit'] / Bytes_to_MB
    usage_ram = dict_quotas['system']['cyclades.ram']['usage'] / Bytes_to_MB
    pending_ram = dict_quotas['system']['cyclades.ram']['pending'] / Bytes_to_MB
    available_ram = (limit_ram-usage_ram-pending_ram)

    limit_vm = dict_quotas['system']['cyclades.vm']['limit']
    usage_vm = dict_quotas['system']['cyclades.vm']['usage']
    pending_vm = dict_quotas['system']['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm

    quotas = {'cpus': {'limit': limit_cpu, 'available': available_cpu},
              'ram': {'limit': limit_ram, 'available': available_ram},
              'disk': {'limit': limit_cd,
                       'available': available_cyclades_disk_GB},
              'cluster_size': {'limit': limit_vm, 'available': available_vm}}
    logging.info(quotas)
    return quotas


def get_flavor_id(token):
    '''From kamaki flavor list get all possible flavors '''
    auth = check_credentials(token, auth_url)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    try:
        flavor_list = cyclades.list_flavors(True)
    except Exception:
        logging.exception('Could not get list of flavors')
        sys.exit(error_flavor_list)
    cpu_list = []
    ram_list = []
    disk_list = []
    disk_template_list = []

    for flavor in flavor_list:
        if flavor['vcpus'] not in cpu_list:
            cpu_list.append(flavor['vcpus'])
        if flavor['ram'] not in ram_list:
            ram_list.append(flavor['ram'])
        if flavor['disk'] not in disk_list:
            disk_list.append(flavor['disk'])
        if flavor['SNF:disk_template'] not in disk_template_list:
            disk_template_list.append(flavor['SNF:disk_template'])
    cpu_list = sorted(cpu_list)
    ram_list = sorted(ram_list)
    disk_list = sorted(disk_list)
    flavors = {'cpus': cpu_list, 'ram': ram_list,
               'disk': disk_list, 'disk_template': disk_template_list}
    logging.info(flavors)
    return flavors


def retrieve_ClusterCreationParams(user):
    '''
    Retrieves user quotas and flavor list from kamaki
    using get_flavor_id and check_quota methods and returns the updated
    ClusterCreationParams model.
    '''
    i = 0
    j = 1
    vms_av = []
    okeanos_token = user.okeanos_token
    flavors = get_flavor_id(okeanos_token)
    quotas = check_quota(okeanos_token)

    vms_max = quotas['cluster_size']['limit']
    vms_available = quotas['cluster_size']['available']
    for i in range(vms_available):
        vms_av.append(j)
        j = j +1
    cpu_max = quotas['cpus']['limit']
    cpu_av = quotas['cpus']['available']
    mem_max = quotas['ram']['limit']
    mem_av = quotas['ram']['available']
    disk_max = quotas['disk']['limit']
    disk_av = quotas['disk']['available']
    cpu_choices = flavors['cpus']
    mem_choices = flavors['ram']
    disk_choices = flavors['disk']
    disk_template = flavors['disk_template']
    os_choices = ['Debian Base']

    # Create a ClusterCreationParams object with the parameters returned from
    # get_flavor_id and check_quota.
    cluster_creation_params = ClusterCreationParams(user_id=user,
                                                    vms_max=vms_max,
                                                    vms_av=vms_av,
                                                    cpu_max=cpu_max,
                                                    cpu_av=cpu_av,
                                                    mem_max=mem_max,
                                                    mem_av=mem_av,
                                                    disk_max=disk_max,
                                                    disk_av=disk_av,
                                                    cpu_choices=cpu_choices,
                                                    mem_choices=mem_choices,
                                                    disk_choices=disk_choices,
                                                    disk_template=disk_template,
                                                    os_choices=os_choices)
    # Return the ClusterCreationParams object
    return cluster_creation_params
