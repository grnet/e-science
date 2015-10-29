#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Methods for getting the list of resources of all user projects
and update the ClusterCreationParams model.

@author: e-science Dev-team
"""
import logging
import cStringIO
import subprocess
from kamaki.clients import ClientError
from django_db_after_login import *
from backend.models import ClusterCreationParams, ClusterInfo, UserInfo
from cluster_errors_constants import *
from okeanos_utils import get_flavor_lists, check_credentials, check_quota, check_images
from authenticate_user import unmask_token, encrypt_key

def ssh_key_list(token):
    """
    Get the ssh_key dictionary of a user
    """   
    
    command = 'curl -X GET -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: ' \
                +  token + '" https://cyclades.okeanos.grnet.gr/userdata/keys'
    # get ssh_keys from okeanos server
    p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE , shell = True)
    out, err = p.communicate()
     # out is in string format and it might have more than one entries so we manually convert it to a easier to use
    output = out[2:-2].split('}, {') # [2:-2] removes [{ from the start of the string and }] from the end
                                     # split('}, {') make the string into a list o of dictionaries if multiple entries exists  they are separated with }, { into different elements
    ssh_dict = list()
    ssh_counter = 0
    for dictionary in output:
        mydict = dict()
        new_dictionary = dictionary.replace('"','') # When returned from curl get request each key:value pair is inside  "" which we do not need so we remove those
        dict1 = new_dictionary.split(', ') # create a list in which each element is key: value
        for each in dict1:
            list__keys_values_in_dict = each.split(': ') # separate key from value as elements of a list
            new_list_of_dict_elements = list()
            for item in list__keys_values_in_dict:
                new_list_of_dict_elements.append(item) # create a list of lists with key value elements
            if len(new_list_of_dict_elements) > 1:
                for pair in new_list_of_dict_elements:
                    mydict[new_list_of_dict_elements[0]] = new_list_of_dict_elements[1] # create a dictionary with key calue pairs
        ssh_dict.append(mydict)  # creates a list of ssh dictionaries       
    return ssh_dict


def project_list_flavor_quota(user):
    """Creates the list of resources for every project a user has quota"""
    okeanos_token = unmask_token(encrypt_key, user.okeanos_token)
    list_of_resources = list()
    flavors = get_flavor_lists(okeanos_token)
    auth = check_credentials(okeanos_token)
    ssh_info = ssh_key_list(okeanos_token)
    ssh_keys_names =list()
    dict_quotas = auth.get_quotas()
    try:
        list_of_projects = auth.get_projects(state='active')
    except ClientError:
        msg = ' Could not get list of projects'
        raise ClientError(msg, error_get_list_projects)
    # Id for ember-data, will use it for store.push the different projects
    ember_project_id = 1
    for item in ssh_info: # find the names of available ssh keys
        if item.has_key('name'):
            ssh_keys_names.append(item['name'])
    for project in list_of_projects:
        # Put system project in the first place of project list
        if project['name'] == 'system:'+str(project['id']):
            list_of_projects.remove(project)
            list_of_projects.insert(0,project)
    for project in list_of_projects:   
        if project['id'] in dict_quotas:
            quotas = check_quota(okeanos_token, project['id'])
            images = check_images(okeanos_token, project['id'])
            list_of_resources.append(retrieve_ClusterCreationParams(flavors,
                                                                    quotas,
                                                                    images,
                                                                    project['name'],
                                                                    user,
                                                                    ember_project_id,
                                                                    ssh_keys_names))
            ember_project_id = ember_project_id + 1
    return list_of_resources


def retrieve_ClusterCreationParams(flavors, quotas, images, project_name, user, ember_project_id, ssh_keys_names):
    """
    Retrieves user quotas and flavor list from kamaki
    using get_flavor_lists and check_quota methods values as input and returns the updated
    ClusterCreationParams model.
    """
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
    ram_max = quotas['ram']['limit']
    ram_av = quotas['ram']['available']
    disk_max = quotas['disk']['limit']
    disk_av = quotas['disk']['available']
    net_av = quotas['network']['available']
    floatip_av = quotas['float_ips']['available']
    cpu_choices = flavors['cpus']
    ram_choices = flavors['ram']
    disk_choices = flavors['disk']
    disk_template = list(flavors['disk_template']) 
    os_choices = images
    for position ,element in enumerate(disk_template):
        disk_template[position] = storage_template[disk_template[position]]
        
    # Create a ClusterCreationParams object with the parameters returned from
    # get_flavor_lists and check_quota.
    cluster_creation_params = ClusterCreationParams(id=ember_project_id,
                                                    user_id=user,
                                                    project_name=project_name,
                                                    vms_max=vms_max,
                                                    vms_av=vms_av,
                                                    cpu_max=cpu_max,
                                                    cpu_av=cpu_av,
                                                    ram_max=ram_max,
                                                    ram_av=ram_av,
                                                    disk_max=disk_max,
                                                    disk_av=disk_av,
                                                    net_av=net_av,
                                                    floatip_av=floatip_av,
                                                    cpu_choices=cpu_choices,
                                                    ram_choices=ram_choices,
                                                    disk_choices=disk_choices,
                                                    disk_template=disk_template,
                                                    os_choices=os_choices,
                                                    ssh_keys_names=ssh_keys_names)
    # Return the ClusterCreationParams object
    return cluster_creation_params
