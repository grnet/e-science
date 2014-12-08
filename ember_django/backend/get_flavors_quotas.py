#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Methods for getting the list of resources of all user projects
and update the ClusterCreationParams model.

@author: Ioannis Stenos, Nick Vrionis
'''

from os.path import join, dirname, abspath
import sys
import logging
sys.path.append(join(dirname(abspath(__file__)), '../..'))
sys.path.append(join(dirname(abspath(__file__)), '..'))
from okeanos_utils import *
from backend.models import ClusterCreationParams
from cluster_errors_constants import *


def project_list_flavor_quota(user):
    """Creates the list of resources for every project a user has quota"""
    okeanos_token = user.okeanos_token
    list_of_resources = []
    flavors = get_flavor_id(okeanos_token)
    auth = check_credentials(okeanos_token)
    dict_quotas = auth.get_quotas()
    try:
        list_of_projects = auth.get_projects(state='active')
        if list_of_projects[0]['name'] != 'system:' + list_of_projects[0]['id']:
            for project in list_of_projects:
                if project['name'] == 'system:' + project['id']:
                    list_of_projects.remove(project)
                    list_of_projects.insert(0, project)
                    break
    except Exception:
        logging.error(' Could not get list of projects')
        sys.exit(error_get_list_projects)

    for project in list_of_projects:
        if project['id'] in dict_quotas:
            quotas = check_quota(okeanos_token, project['id'])
            list_of_resources.append(retrieve_ClusterCreationParams(flavors, quotas, project['name'], user))
    return list_of_resources


def retrieve_ClusterCreationParams(flavors, quotas, project_name, user):
    '''
    Retrieves user quotas and flavor list from kamaki
    using get_flavor_id and check_quota methods and returns the updated
    ClusterCreationParams model.
    '''
    i = 0
    j = 1
    vms_av = []
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
                                                    project_name=project_name,
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
