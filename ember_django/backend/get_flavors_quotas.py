#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Methods for getting the list of resources of all user projects
and update the ClusterCreationParams model.

@author: Ioannis Stenos, Nick Vrionis
"""
import logging
import cStringIO
import subprocess
from kamaki.clients import ClientError
from orka.okeanos_utils import *
from django_db_after_login import *
from backend.models import ClusterCreationParams, ClusterInfo, UserInfo
from orka.cluster_errors_constants import *

def ssh_list(token):
    """
    Get the ssh_key dictionary of a user
    """
    
    command = 'curl -X GET -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: ' + token + '" https://cyclades.okeanos.grnet.gr/userdata/keys'
    p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE , shell = True)
    out, err = p.communicate()
    output = out[2:-2].split('}, {')
    ssh_dict =list()
    ssh_counter = 0
    for dictionary in output:
        mydict=dict()
        new = dictionary.replace('"','')
        d1 = new.split(', ')
        for every in d1:
            z=every.split(': ')
            z1=list()
            for item in z:
                z1.append(item)
            if len(z1) > 1:
                for k in z1:
                    mydict[z1[0]]=z1[1]
        ssh_dict.append(mydict)        
    # print ssh_dict[0]['name']   
    return ssh_dict


def project_list_flavor_quota(user):
    """Creates the list of resources for every project a user has quota"""
    okeanos_token = user.okeanos_token
    list_of_resources = list()
    flavors = get_flavor_id(okeanos_token)
    auth = check_credentials(okeanos_token)
    ssh_info = ssh_list(okeanos_token)
    ssh_keys_names =list()
    dict_quotas = auth.get_quotas()
    try:
        list_of_projects = auth.get_projects(state='active')
    except ClientError:
        msg = ' Could not get list of projects'
        raise ClientError(msg, error_get_list_projects)
    # Id for ember-data, will use it for store.push the different projects
    ember_project_id = 1
    ssh_info = ssh_list(okeanos_token)
    for item in ssh_info:
        if item.has_key('name'):
            ssh_keys_names.append(item['name'])
    for project in list_of_projects:
        if project['name'] == 'system:'+str(project['id']):
            list_of_projects.remove(project)
            list_of_projects.insert(0,project)
    for project in list_of_projects:   
        if project['id'] in dict_quotas:
            quotas = check_quota(okeanos_token, project['id'])
            list_of_resources.append(retrieve_ClusterCreationParams(flavors,
                                                                    quotas,
                                                                    project['name'],
                                                                    user,
                                                                    ember_project_id,
                                                                    ssh_keys_names))
            ember_project_id = ember_project_id + 1
    
    return list_of_resources


def retrieve_pending_clusters(token, project_name):
    """Retrieve pending cluster info"""
    uuid = get_user_id(token)
    pending_quota = {"VMs": 0, "Cpus": 0, "Ram": 0, "Disk": 0, "Ip": 0,
                     "Network": 0}
    user = UserInfo.objects.get(uuid=uuid)
    # Get clusters with pending status
    pending_clusters = ClusterInfo.objects.filter(user_id=user,
                                                  project_name=project_name,
                                                  cluster_status="2")
    if pending_clusters:
        # Get all pending resources
        # excluding ip and network (always zero pending as a convention
        # for the time being)
        vm_sum, vm_cpu, vm_ram, vm_disk = 0, 0, 0, 0
        for cluster in pending_clusters:
            vm_sum = vm_sum + cluster.cluster_size
            vm_cpu = vm_cpu + cluster.cpu_master + cluster.cpu_slaves*(cluster.cluster_size - 1)
            vm_ram = vm_ram + cluster.mem_master + cluster.mem_slaves*(cluster.cluster_size - 1)
            vm_disk = vm_disk + cluster.disk_master + cluster.disk_slaves*(cluster.cluster_size - 1)

        pending_quota = {"VMs": vm_sum, "Cpus": vm_cpu, "Ram": vm_ram,
                         "Disk": vm_disk, "Ip": 0,
                         "Network": 0}

    return pending_quota


def retrieve_ClusterCreationParams(flavors, quotas, project_name, user, ember_project_id,ssh_keys_names):
    """
    Retrieves user quotas and flavor list from kamaki
    using get_flavor_id and check_quota methods and returns the updated
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
    cluster_creation_params = ClusterCreationParams(id=ember_project_id,
                                                    user_id=user,
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
                                                    os_choices=os_choices,
                                                    ssh_keys_names=ssh_keys_names
                                                    )
    # Return the ClusterCreationParams object
    return cluster_creation_params
