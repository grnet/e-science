#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains useful classes and fuctions for orka package.

@author: e-science Dev-team
"""
import logging
import re
import subprocess
import yaml
import urllib
import requests
from urllib2 import urlopen, Request, HTTPError
from base64 import b64encode
from os import devnull
from os.path import abspath, join, expanduser, basename
from kamaki.clients import ClientError
from kamaki.clients.image import ImageClient
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesClient, CycladesNetworkClient
from time import sleep
from datetime import datetime
from cluster_errors_constants import *
from celery import current_task
from authenticate_user import unmask_token, encrypt_key
from django_db_after_login import db_cluster_update, db_cluster_delete, get_user_id, db_server_update, db_hadoop_update, db_dsl_create, db_dsl_update, db_dsl_delete
from backend.models import UserInfo, ClusterInfo, VreServer, Dsl, OrkaImage, VreImage


def retrieve_pending_clusters(token, project_name):
    """Retrieve pending cluster info"""
    uuid = get_user_id(token)
    pending_quota = {"VMs": 0, "Cpus": 0, "Ram": 0, "Disk": 0, 
                     "Ip": 0, "Network": 0}
    user = UserInfo.objects.get(uuid=uuid)
    # Get clusters with pending status
    pending_clusters = ClusterInfo.objects.filter(user_id=user,
                                                  project_name=project_name,
                                                  cluster_status=const_cluster_status_pending)
    if pending_clusters:
        # Get all pending resources
        # excluding IP and network (always zero pending as a convention for the time being)
        vm_sum, vm_cpu, vm_ram, vm_disk = 0, 0, 0, 0
        for cluster in pending_clusters:
            vm_sum = vm_sum + cluster.cluster_size
            vm_cpu = vm_cpu + cluster.cpu_master + cluster.cpu_slaves*(cluster.cluster_size - 1)
            vm_ram = vm_ram + cluster.ram_master + cluster.ram_slaves*(cluster.cluster_size - 1)
            vm_disk = vm_disk + cluster.disk_master + cluster.disk_slaves*(cluster.cluster_size - 1)

        pending_quota = {"VMs": vm_sum, "Cpus": vm_cpu, "Ram": vm_ram, "Disk": vm_disk, 
                         "Ip": 0, "Network": 0}

    return pending_quota

def set_cluster_state(token, cluster_id, state, status='Pending', master_IP='', password='', error=''):
    """
    Logs a cluster state message and updates the celery and escience database
    state.
    """
    logging.log(SUMMARY, state)
    db_cluster_update(token, status, cluster_id, master_IP, state=state, password=password, error=error)
    if len(state) >= const_truncate_limit:
        state = state[:(const_truncate_limit-2)] + '..'
    current_task.update_state(state=state)
    
    
def set_server_state(token, id, state, status='Pending', server_IP='', okeanos_server_id='', password='', error=''):
    """
    Logs a VRE server state message and updates the celery and escience database
    state.
    """
    logging.log(SUMMARY, state)
    db_server_update(token, status, id, server_IP, state=state, okeanos_server_id=okeanos_server_id, password=password, error=error)
    if len(state) >= const_truncate_limit:
        state = state[:(const_truncate_limit-2)] + '..'
    current_task.update_state(state=state)


def parse_hdfs_dest(regex, path):
    """
    Parses remote hdfs directory for the orka put command to check if directory exists.
    """
    parsed_path = re.match(regex, path)
    if parsed_path:
        return parsed_path.group(1)
    else:
        return parsed_path


def get_project_id(token, project_name):
    """
    Return the id of an active ~okeanos project.
    """
    auth = check_credentials(token)
    dict_quotas = auth.get_quotas()
    try:
        list_of_projects = auth.get_projects(state='active')
    except ClientError:
        msg = ' Could not get list of active projects'
        raise ClientError(msg, error_get_list_projects)
    for project in list_of_projects:
        if project['name'] == project_name and project['id'] in dict_quotas:
            return project['id']
    msg = ' No project id was found for ' + project_name
    raise ClientError(msg, error_project_id)


def destroy_server(token, id):
    """Destroys a VRE server in ~okeanos ."""
    current_task.update_state(state="Started")
    vre_server = VreServer.objects.get(id=id)    
    auth = check_credentials(unmask_token(encrypt_key,token))
    current_task.update_state(state="Authenticated")
    set_server_state(token, id, 'Deleting VRE server and its public IP')
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], unmask_token(encrypt_key,token))
    nc = init_cyclades_netclient(endpoints['network'], unmask_token(encrypt_key,token))
    cyclades.delete_server(vre_server.server_id)
    new_status = cyclades.wait_server(vre_server.server_id,current_status='ACTIVE',max_wait=MAX_WAIT)
    if new_status != 'DELETED':
        state = 'Error while deleting VRE server'
        set_server_state(token, id, state,status='Destroyed')
        raise ClientError('Error while deleting VRE server', error_fatal)
    ip_to_delete = get_public_ip_id(nc,vre_server.server_IP)
    nc.delete_floatingip(ip_to_delete['id']) 
    state= 'VRE server {0} and its public IP {1} were deleted'.format(vre_server.server_name,vre_server.server_IP)
    set_server_state(token, id, state, status='Destroyed')
    return vre_server.server_name

def create_dsl(choices):
    """Creates a Reproducible Experiments Metadata  file in Pithos."""
    
    uuid = get_user_id(unmask_token(encrypt_key,choices['token']))
    action_date = datetime.now().replace(microsecond=0)
    cluster = ClusterInfo.objects.get(id=choices['cluster_id'])
    data = {'cluster': {'name': cluster.cluster_name, 'project_name': cluster.project_name, 'image': cluster.os_image, 'disk_template': u'{0}'.format(cluster.disk_template),
                        'size': cluster.cluster_size, 'flavor_master':[cluster.cpu_master, cluster.ram_master,cluster.disk_master], 'flavor_slaves': [cluster.cpu_slaves, cluster.ram_slaves, cluster.disk_slaves]}, 
            'configuration': {'replication_factor': cluster.replication_factor, 'dfs_blocksize': cluster.dfs_blocksize}}
    if not (choices['dsl_name'].endswith('.yml') or choices['dsl_name'].endswith('.yaml')): # give file proper type
        choices['dsl_name'] = '{0}.yaml'.format(choices['dsl_name'])
    task_id = current_task.request.id
    dsl_id = db_dsl_create(choices, task_id)
    yaml_data = yaml.safe_dump(data,default_flow_style=False)
    url = '{0}/{1}/{2}/{3}'.format(pithos_url, uuid, choices['pithos_path'], urllib.quote(choices['dsl_name']))
    headers = {'X-Auth-Token':'{0}'.format(unmask_token(encrypt_key,choices['token'])),'content-type':'text/plain'}
    r = requests.put(url, headers=headers, data=yaml_data) # send file to Pithos
    response = r.status_code
    if response == pithos_put_success:
        db_dsl_update(choices['token'],dsl_id,state='Created',dsl_data=yaml_data)
        return dsl_id, choices['pithos_path'], choices['dsl_name']
    else:
        db_dsl_update(choices['token'],dsl_id,state='Failed')
        msg = "Failed to save experiment metadata %s to %s" % (choices['dsl_name'], choices['pithos_path'])
        raise ClientError(msg, error_pithos_connection)
        
        
def destroy_dsl(token, id):
    """Destroys a Reproducible Experiments Metadata file in Pithos."""
    # just remove from our DB for now
    dsl = Dsl.objects.get(id=id)
    db_dsl_delete(token,id)
    return dsl.id

def import_dsl(choices):
    """Imports a Reproducible Experiments Metadata file from Pithos."""
    
    uuid = get_user_id(unmask_token(encrypt_key,choices['token']))
    url = '{0}/{1}/{2}/{3}'.format(pithos_url, uuid, choices['pithos_path'], urllib.quote(choices['dsl_name']))
    headers = {'X-Auth-Token':'{0}'.format(unmask_token(encrypt_key,choices['token']))}
    request = Request(url, headers=headers)
    try:
        pithos_input_stream = urlopen(request).read()
        task_id = current_task.request.id
        dsl_id = db_dsl_create(choices, task_id)
        db_dsl_update(choices['token'],dsl_id,state='Created',dsl_data=pithos_input_stream)
        return dsl_id, choices['pithos_path'], choices['dsl_name']
    except HTTPError, e:
        raise HTTPError(e, error_import_dsl)


def check_pithos_path(pithos_path):
    """Check given pithos path to be in a specific format."""
    
    if pithos_path.startswith('/'):
        pithos_path = pithos_path[1:]
    if pithos_path.endswith('/'):
        pithos_path = pithos_path[:-1]
    return pithos_path


def check_pithos_object_exists(pithos_path, dsl_name, token):
    """Request to Pithos to see if object exists."""
    
    uuid = get_user_id(unmask_token(encrypt_key,token))
    url = '{0}/{1}/{2}/{3}'.format(pithos_url, uuid, pithos_path, dsl_name)
    headers = {'X-Auth-Token':'{0}'.format(unmask_token(encrypt_key,token))}
    r = requests.head(url, headers=headers)
    response = r.status_code
    return response


def get_pithos_container_info(pithos_path, token):
    """Request to Pithos to see if container exists."""
    
    if '/' in pithos_path:
        pithos_path = pithos_path.split("/", 1)[0]
    uuid = get_user_id(unmask_token(encrypt_key,token))
    url = '{0}/{1}/{2}'.format(pithos_url, uuid, pithos_path)
    headers = {'X-Auth-Token':'{0}'.format(unmask_token(encrypt_key,token))}
    r = requests.head(url, headers=headers)
    response = r.status_code
    return response

def check_cluster_options(cluster_options,dsl,token,map_dsl_to_cluster):
    """Used in replay experiment. Check the passed cluster options have mandatory keys, inject defaults for optionals where necessary."""
    # map yaml key names to cluster creation json payload keys
    dslkeys_to_clusteroptions = {'name':'cluster_name','size':'cluster_size','image':'os_choice',\
                                 'flavor_master':['cpu_master','ram_master','disk_master'],\
                                 'flavor_slaves':['cpu_slaves','ram_slaves','disk_slaves']}
    if map_dsl_to_cluster:
        for (key,value) in dslkeys_to_clusteroptions.iteritems():
            option_val = cluster_options.pop(key,None)
            if option_val is not None:  
                if type(option_val) is list:
                    for i in range(len(value)):
                        if option_val[i] is not None:
                            cluster_options.setdefault(value[i],option_val[i])
                        else:
                            msg = "Mandatory cluster option %s is missing from %s/%s" % (value[i], dsl.dsl_name, key)
                            raise ClientError(msg, error_fatal)
                else:
                    if key=="name":
                        # [orka]- prefix is added automatically in create cluster, remove it if found in name to avoid duplication
                        option_val = option_val[7:] if option_val.startswith("[orka]-") else option_val
                    cluster_options.setdefault(value,option_val)
            else:
                msg = "Mandatory cluster option %s is missing from %s" % (key, dsl.dsl_name)
                raise ClientError(msg, error_fatal)
    # inject options that are not mandatory but should have default values
    # only sets a default if a value has not already been parsed
    cluster_options.setdefault('token',token) # inject the masked token in options.
    cluster_options.setdefault('admin_password','') #inject an empty admin password value if none is parsed
    cluster_options.setdefault('dfs_blocksize','128')
    replication_factor_default = str(min(int(cluster_options['cluster_size'])-1,2))
    cluster_options.setdefault('replication_factor',replication_factor_default)
    return cluster_options


def actions_check_filespec(verb, source, destination):
    """
    Supporting method for replay experiment. Verifies that path is a "pithos protocol" according to action and direction.
    """
    pithos_regex = re.compile("(?iu)((?:^pithos)+?:/)(.+)")
    msg = ''
    filespec = ''
    valid = False
    if verb=="put": # only pithos source supported for orka-Web
        result = pithos_regex.match(source)
        if not result:
            valid = False
            msg = "%s is not a valid source for put action. Only Pithos sources are supported for orka-Web." % source
        else:
            source = result.group(2)
            valid = True
    elif verb=="get": # only pithos destination supported for orka-Web
        result = pithos_regex.match(destination)
        if not result:
            valid = False
            msg = "%s is not a valid destination for get action. Only Pithos destinations are supported for orka-Web." % destination
        else:
            destination = result.group(2)
            valid = True
    return valid, msg, source, destination

def action_put_prepare(user, master_IP, source_file, pub=False):
    """
    Supporting method for replay experiment. 
    Temporary publish a pithos file so we can leverage existing backend methods for remote > hdfs functionality.
    """
    if pub==False:
        str_command = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + \
        "{0}@{1} ".format(user, master_IP) + \
        "\"kamaki file unpublish \'{0}\'\"".format(source_file)
        response = subprocess.call(str_command, stderr=open(devnull,'w'), stdout=open(devnull,'w'), shell=True)
        return response
    
    str_command = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + \
    "{0}@{1} ".format(user,master_IP) + \
    "\"kamaki file publish \'{0}\'\"".format(source_file)
    str_link = subprocess.check_output(str_command, stderr=open(devnull,'w'), shell=True)
    remote_regex = re.compile("(?iu)((?:^ht|^f)+?tps?://)(.+)")
    result = remote_regex.match(str_link)
    if result:
        return result.group(0)
    else:
        return None
    

def check_actions(actions,dsl,token):
    """
    Used in replay experiment. Check that actions are valid verbs in our domain.
    Update the queue with pairs of verb, args preserving order, and return it.
    """
    # start hadoop, stop hadoop, format HDFS, add cluster node, remove cluster node, 
    # put file on HDFS, get file from HDFS, run command on cluster
    valid_verbs = ["start","stop","format","node_add","node_remove","put","get","run_job"]
    verb_regex = re.compile("^(\w+)(?:\s*)(.*)",re.IGNORECASE) # use a non-capturing group to remove the whitespace between verb, args
    for i in range(len(actions)):
        action_parse = verb_regex.match(actions[i])
        if action_parse:
            verb = action_parse.group(1)
            args = action_parse.group(2)
            if verb not in valid_verbs:
                msg = '%s is not a valid action for Experiment Replay through orka Web.' % verb
                raise ClientError(msg, error_fatal)
            if verb in ['put','get']:
                source, destination = args.strip('()').split(',')
                valid, msg, source, destination = actions_check_filespec(verb, source, destination)
                if not valid:
                    raise ClientError(msg, error_fatal)
                args = [source,destination]
            actions.pop(i)
            actions.insert(i,{verb:args})
        else:
            msg = 'Could not parse an action out of %s' % actions[i]
            raise ClientError(msg, error_fatal)
    return actions

def action_continue(token, dsl_id, task, msg):
    """
    Replay experiment helper function.
    Wrap task and db updates for success in an easy call.
    """
    task.update_state(state=msg)
    db_dsl_update(token,dsl_id,dsl_status=const_experiment_status_replay,state=msg)

def action_stop(token, dsl_id, task, msg):
    """
    Replay experiment helper function.
    Wrap task and db update for failure in an easy call.
    """
    task.update_state(state=msg)
    db_dsl_update(token,dsl_id,dsl_status=const_experiment_status_atrest,state=msg)

def replay_dsl(token, id):
    """Replays an experiment on cluster defined or created through parameters and plays actions in sequence"""
    dsl = Dsl.objects.get(id=id)
    # pre execution checks
    dsl_data_yaml = dsl.dsl_data
    state_msg = 'Checking experiment metadata'
    action_continue(token, id, current_task, state_msg)
    try:
        dsl_data_dict = yaml.safe_load(dsl_data_yaml)
    except yaml.YAMLError, e:
        msg = 'Error parsing experiment .yaml file %s' % e
        action_stop(token, id, current_task, msg)
        raise ClientError(msg,error_fatal)
    cluster_options = dsl_data_dict.get('cluster',{})
    if len(cluster_options)<=0:
        msg = 'No cluster options found in %s. Cannot proceed.' % dsl.dsl_name
        action_stop(token, id, current_task, msg)
        raise ClientError(msg,error_fatal)
    cluster_options.update(dsl_data_dict.get('configuration',{}))
    # check if there are cluster_id, master_IP cluster options in the yaml, verify cluster exists and is active, 
    # if exists and active skip creation, if not active get specs and replicate then proceed with created cluster, else abort.
    skip_cluster_create = False
    map_dsl_to_cluster = True
    cluster_id_for_replay = None
    if "cluster_id" in cluster_options:
        if ClusterInfo.objects.filter(id=cluster_options['cluster_id']).exists():
            cluster_to_check = ClusterInfo.objects.filter(id=cluster_options['cluster_id'])
            if cluster_to_check.values_list('cluster_status',flat=True)[0]==const_cluster_status_active:
                skip_cluster_create = True
                cluster_id_for_replay = cluster_options['cluster_id']
                msg = 'Cluster exists and is active, skipping cluster creation'
                action_continue(token, id, current_task, msg)
            else:
                cluster_options = cluster_to_check.values('cluster_name','cluster_size',\
                                                          'cpu_master','ram_master','disk_master',\
                                                          'cpu_slaves','ram_slaves','disk_slaves',\
                                                          'disk_template','os_image','project_name',\
                                                          'replication_factor','dfs_blocksize')[0]
                os_choice = cluster_options.pop('os_image',None)
                cluster_options.setdefault('os_choice',os_choice)
                cluster_name = cluster_options.pop('cluster_name',None)
                cluster_name = cluster_name[7:] if cluster_name.startswith("[orka]-") else cluster_name
                cluster_options.setdefault('cluster_name',cluster_name)
                cluster_options.pop('cluster_id',None)
                cluster_options.pop('master_IP',None)
                map_dsl_to_cluster = False
                msg = 'Cluster exists but is not active. Using it as blueprint for a new one.'
                action_continue(token, id, current_task, msg)
        else:
            msg = 'Cluster id and master IP given do not match any clusters. Cannot proceed.'
            action_stop(token, id, current_task, msg)
            raise ClientError(msg,error_fatal)
            
    if not skip_cluster_create:
        try:
            cluster_options = check_cluster_options(cluster_options,dsl,token,map_dsl_to_cluster)
        except ClientError,e:
            msg = str(e.args[0])
            action_stop(token, id, current_task, msg)
            raise e
        # cluster section
        # only need to import create cluster if we are going to be making a cluster
        from backend.create_cluster import YarnCluster
        state_msg = 'Started experiment cluster creation'
        action_continue(token, id, current_task, state_msg)
        c_cluster = YarnCluster(cluster_options)
        MASTER_IP, servers, password, cluster_id = c_cluster.create_yarn_cluster()
        if cluster_id > 0:
            state_msg = 'Experiment cluster created successfully'
            action_continue(token, id, current_task, state_msg)
            cluster_id_for_replay = cluster_id
        else:
            state_msg = 'Experiment cluster creation failed'
            action_stop(token, id, current_task, state_msg)
            raise ClientError(state_msg, error_fatal)
    
    # actions section
    actions = dsl_data_dict.get('actions',[])
    if len(actions)>0 and cluster_id_for_replay is not None:
        try:
            actions = check_actions(actions, dsl, token)
        except ClientError,e:
            msg = str(e.args[0])
            action_stop(token, id, current_task, msg)
            raise e
        # we have actions back in an array with cmd:params pairs
        for action in actions:
            cluster = ClusterInfo.objects.get(id=cluster_id_for_replay)
            for cmd,params in action.iteritems():
                if cmd in ["start","stop","format"]:
                    # import cluster management methods
                    from backend.run_ansible_playbooks import ansible_manage_cluster
                    msg = 'Action: Hadoop %s' % cmd
                    action_continue(token, id, current_task, msg)
                    ansible_manage_cluster(cluster_id_for_replay,cmd)
                elif cmd == "node_add":
                    msg = 'Action: Cluster %s' % cmd
                    action_continue(token, id, current_task, msg)
                    scale_cluster(token, cluster_id_for_replay, 1)
                elif cmd == "node_remove":
                    msg = 'Action: Cluster %s' % cmd
                    action_continue(token, id, current_task, msg)
                    scale_cluster(token, cluster_id_for_replay, -1)
                elif cmd in ['put','get']:
                    source, destination = params[0], params[1]
                    if (cluster.cluster_status != const_cluster_status_active) or (cluster.hadoop_status != const_hadoop_status_started):
                        msg = 'Action Error: HDFS operations are only possible on an active cluster with Hadoop started.'
                        action_stop(token, id, current_task, msg)
                        raise ClientError(msg, error_fatal)
                    msg = 'Action: HDFS %s with source %s and destination %s' % (cmd,source,destination)
                    action_continue(token, id, current_task, msg)
                    if cmd == "put": # put from pithos to hdfs
                        from backend.reroute_ssh import HdfsRequest
                        new_source = action_put_prepare(DEFAULT_HADOOP_USER, cluster.master_IP, source, True)
                        source_path = source.split("/")
                        source_filename = source_path[len(source_path)-1]
                        new_destination = destination.endswith("/") and "%s%s" % (destination,source_filename) or destination
                        if new_source:
                            file_put_request = HdfsRequest({'user':'','password':'','master_IP':cluster.master_IP,'source':new_source,'dest':new_destination})
                            try: 
                                result = file_put_request.put_file_hdfs()
                            except RuntimeError, e:
                                msg = str(e.args[0])
                                action_stop(token, id, current_task, msg)
                                raise ClientError(msg,error_fatal)
                            action_put_prepare(DEFAULT_HADOOP_USER, cluster.master_IP, source)
                            if result == 0:
                                msg = "Action Result: Success"
                                action_continue(token, id, current_task, msg)
                            else:
                                msg = "Action Error: %s %s %s" % (cmd, source, destination)
                                action_stop(token, id, current_task, msg)
                                raise ClientError(msg,error_ssh_client)
                    elif cmd == "get": # get from hdfs to pithos
                        try:
                            file_exists = subprocess.call("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + \
                                                           "{0}@{1}".format(DEFAULT_HADOOP_USER,cluster.master_IP) + \
                                                           " \'/usr/local/hadoop/bin/hdfs dfs -test -e " + "\'{0}\'".format(source) + "\'", \
                                                           stderr=open(devnull,'w'), shell=True)
                            if file_exists == 0:
                                from orka.utils import from_hdfs_to_pithos
                                from_hdfs_to_pithos(DEFAULT_HADOOP_USER, cluster.master_IP, source, destination)
                            else:
                                msg = 'Action Error: Source file %s not found.' % source
                                action_stop(token, id, current_task, msg)
                                raise ClientError(msg, error_fatal)
                        except Exception, e:
                            msg = str(e.args[0])
                            action_stop(token, id, current_task, msg)
                            raise ClientError(msg, error_fatal)
                elif cmd == "run_job":
                    from backend.reroute_ssh import establish_connect, exec_command, MASTER_SSH_PORT
                    remote_user, remote_cmd = params.strip('()').split(',')
                    remote_cmd = remote_cmd.strip('\" ')
                    try:
                        ssh_client = establish_connect(cluster.master_IP,remote_user,'',MASTER_SSH_PORT)
                    except RuntimeError, e:
                        msg = 'Failed connecting to %s as %s' % (cluster.master_IP, remote_user)
                        action_stop(token, id, current_task, msg)
                        raise ClientError(msg,error_ssh_client)
                    msg = 'Action: Hadoop %s with command %s as remote user %s' % (cmd,remote_cmd,remote_user)
                    action_continue(token, id, current_task, msg)
                    try:
                        ex_status = exec_command(ssh_client, remote_cmd, command_state='celery task')
                    except Exception, e:
                        msg = 'Action Error: %s' % str(e.args[0])
                        action_stop(token, id, current_task, msg)
                        raise ClientError(msg,error_ssh_client)
                    msg = 'Action Succeeded'
                    action_continue(token, id, current_task, msg)
                   
    current_task.update_state(state='Finished')
    db_dsl_update(token,id,dsl_status=const_experiment_status_atrest,state='Finished')
    return dsl.id
    

def get_public_ip_id(cyclades_network_client,float_ip):  
    """Return IP dictionary of an ~okeanos public IP"""
    list_of_ips = cyclades_network_client.list_floatingips()
    for ip in list_of_ips:
        if ip['floating_ip_address'] == float_ip:
            return ip

def check_scale_cluster_up(token, cluster_id, cluster_to_scale):
    """
    Check user quota if new node can be added to existing cluster.
    Return tuple with message and value
    """
    project_id = get_project_id(unmask_token(encrypt_key,token), cluster_to_scale.project_name)
    quotas = check_quota(unmask_token(encrypt_key,token), project_id)
    # The new node will be a slave node and will have the same flavor combination with the existing nodes of the cluster
    if quotas['ram']['available'] < cluster_to_scale.ram_slaves:
        msg = 'Not enough ram for new node.'
        set_cluster_state(token, cluster_id, state=msg)
        return (msg, error_quotas_ram)
    if quotas['cpus']['available'] < cluster_to_scale.cpu_slaves:
        msg = 'Not enough cpu for new node.'
        set_cluster_state(token, cluster_id, state=msg)
        return (msg, error_quotas_cpu)
    if quotas['disk']['available'] < cluster_to_scale.disk_slaves:
        msg = 'Not enough disk for new node.'
        set_cluster_state(token, cluster_id, state=msg)
        return (msg, error_quotas_cyclades_disk)
    return ('SUCCESS',0)
    
def cluster_add_node(token, cluster_id, cluster_to_scale, cyclades, netclient, plankton, status):
    """
    Create a VM in ~okeanos and attach it to the network of the requested cluster.
    """
    new_slave = {}
    server_home_path = expanduser('~')
    server_ssh_keys = join(server_home_path, ".ssh/id_rsa.pub")
    pub_keys_path = ''
    project_id = get_project_id(unmask_token(encrypt_key,token), cluster_to_scale.project_name)
    node_name = cluster_to_scale.cluster_name + '-' + str(cluster_to_scale.cluster_size + 1) # name of new node should follow the naming convention of the rest nodes in the cluster
    state = "Adding new datanode {0}".format(node_name)
    set_cluster_state(token, cluster_id, state)
    try:
        flavor_list = cyclades.list_flavors(True)
    except ClientError:
        msg = 'Could not get list of flavors'
        raise ClientError(msg, error_flavor_list)
    for flavor in flavor_list: # The new node will be a slave node and will have the same flavor combination with the existing nodes of the cluster
        if flavor['ram'] == cluster_to_scale.ram_slaves and \
                            flavor['SNF:disk_template'] == cluster_to_scale.disk_template and \
                            flavor['vcpus'] == cluster_to_scale.cpu_slaves and \
                            flavor['disk'] == cluster_to_scale.disk_slaves:
                flavor_id = flavor['id']
    chosen_image = {}
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the operating system arg given
    for lst in list_current_images: # new node should have the same image as the other cluster nodes
        if lst['name'] == cluster_to_scale.os_image:
            chosen_image = lst
            chosen_image_id = chosen_image['id']
    if not chosen_image:
        msg = ' Image not found.'
        raise ClientError(msg, error_image_id)

    master_id = None
    network_to_edit_id = None
    new_status = 'placeholder'
    # Get master virtual machine and network from IP   
    ip = get_public_ip_id(netclient, cluster_to_scale.master_IP)
    master_id = ip['instance_id']          
    master_server = cyclades.get_server_details(master_id)
    for attachment in master_server['attachments']:
        if (attachment['OS-EXT-IPS:type'] == 'fixed' and not attachment['ipv6']):
           network_to_edit_id = attachment['network_id']
           break
    # Create new node with create server methode of cyclades     
    new_server = cyclades.create_server(node_name, flavor_id, chosen_image_id,
                                        personality=personality(server_ssh_keys,pub_keys_path),
                                        networks=[{"uuid": network_to_edit_id}], project_id=project_id)

    new_status = cyclades.wait_server(new_server['id'], max_wait=MAX_WAIT)
    if new_status != 'ACTIVE':
        msg = ' Status for server [%s] is %s. Server will be deleted' % \
            (servers[i]['name'], new_status)
        cyclades.delete_server(new_server['id'])
        raise ClientError(msg, error_create_server)
    cluster_to_scale.cluster_size = cluster_to_scale.cluster_size + 1 # new cluster size
    cluster_to_scale.save()
    new_slave_private_ip = '192.168.0.{0}'.format(str(1 + cluster_to_scale.cluster_size)) # Add new node to network
    new_slave_port = ADD_TO_GET_PORT + cluster_to_scale.cluster_size
    state = "New datanode {0} was added to cluster network".format(node_name)
    set_cluster_state(token, cluster_id, state, status='Active')
    new_slave = {'id':new_server['id'], 'fqdn': new_server['SNF:fqdn'],'private_ip': new_slave_private_ip,
                 'password': new_server['adminPass'],'port': new_slave_port,'uuid': new_server['user_id'],
                 'image_id':new_server['image']['id']}
    return new_slave

def find_node_to_remove(cluster_to_scale, cyclades, netclient):
    """
    Find last node from cluster and return hostname
    and ~okeanos id of the node.
    """
    node_id = None
    cluster_servers = []
    list_of_servers = cyclades.list_servers(detail=True)
    ip = get_public_ip_id(netclient, cluster_to_scale.master_IP)
    master_id = ip['instance_id']          
    master_server = cyclades.get_server_details(master_id)
    for attachment in master_server['attachments']:
         if (attachment['OS-EXT-IPS:type'] == 'fixed' and not attachment['ipv6']):
            network_id = attachment['network_id']
            break
    for server in list_of_servers:
        for attachment in server['attachments']:
            if attachment['network_id'] == network_id:
                cluster_servers.append(server)
                break
    for server in cluster_servers:
        node_id = server['id']
        node_fqdn = server['SNF:fqdn']
    return node_fqdn,node_id

def cluster_remove_node(node_fqdn, node_id, token, cluster_id, cluster_to_scale, cyclades, status):
    """Remove a node of a scaled down cluster."""
    state = "Deleting Node %s from cluster %s (id:%d)" % (node_fqdn, cluster_to_scale.cluster_name, cluster_id)
    set_cluster_state(token, cluster_id, state)
    cyclades.delete_server(node_id)    
    new_status = cyclades.wait_server(node_id,current_status='ACTIVE',max_wait=MAX_WAIT)
    if new_status != 'DELETED':
        msg = 'Error deleting server [%s]' % node_fqdn
        logging.error(msg)
        set_cluster_state(token, cluster_id, state=msg, status=status, error=msg)
        raise ClientError(msg, error_cluster_corrupt)
    state = 'Deleted Node %s from cluster %s (id:%d)' % (node_fqdn, cluster_to_scale.cluster_name, cluster_id)
    cluster_to_scale.cluster_size -= 1 # New cluster size.
    cluster_to_scale.save()
    set_cluster_state(token, cluster_id, state, status='Active')
    

def rollback_scale_cluster(list_of_slaves, cyclades, cluster_to_scale, size, ansible=False):
    """
    Rollback cluster when scale add node fail. More rollback actions when ansible has failed during
    hadoop configurations for the new nodes.
    """
    from run_ansible_playbooks import modify_ansible_hosts_file,ansible_scale_cluster
    cluster_name_suffix_id = '{0}-{1}'.format(cluster_to_scale.cluster_name, cluster_to_scale.id)
    for slave in list_of_slaves:
        cyclades.delete_server(slave['id'])
    if ansible:
        for slave in list_of_slaves:
            modify_ansible_hosts_file(cluster_name_suffix_id, action='remove_slaves', slave_hostname=slave['fqdn'])           
        ansible_hosts = modify_ansible_hosts_file(cluster_name_suffix_id, action='join_slaves')
        ansible_scale_cluster(ansible_hosts, action='rollback_scale_cluster')
    cluster_to_scale.cluster_size = size
    cluster_to_scale.save()


def scale_cluster(token, cluster_id, cluster_delta, status='Pending'):
    """
    Scales an active cluster by cluster_delta (signed int).
    For scaling up finds the cluster settings and last internal ip/port slave
    and "appends" cluster_delta nodes.
    For scaling down it removes the last slave. 
    """
    from reroute_ssh import reroute_ssh_to_slaves
    from run_ansible_playbooks import modify_ansible_hosts_file,ansible_scale_cluster,ansible_manage_cluster
    cluster_to_scale = ClusterInfo.objects.get(id=cluster_id)
    pre_scale_size = cluster_to_scale.cluster_size
    previous_cluster_status = cluster_to_scale.cluster_status
    previous_hadoop_status = cluster_to_scale.hadoop_status
    status_map = {"0":"Destroyed","1":"Active","2":"Pending","3":"Failed"}
    # pre-flight checks. If cluster status is pending or hadoop status formatting abort.
    if (previous_cluster_status == const_cluster_status_pending) or (previous_hadoop_status == const_hadoop_status_format):
        current_task.update_state(state="Skipping")
        return cluster_to_scale.cluster_name
    # pre-flight checks done
    current_task.update_state(state="Started")
    auth = check_credentials(unmask_token(encrypt_key,token))
    current_task.update_state(state="Authenticated")
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], unmask_token(encrypt_key,token))
    netclient = init_cyclades_netclient(endpoints['network'], unmask_token(encrypt_key,token))
    plankton = init_plankton(endpoints['plankton'], unmask_token(encrypt_key,token))
    state = ''
    list_of_new_slaves = []
    cluster_name_suffix_id = '{0}-{1}'.format(cluster_to_scale.cluster_name, cluster_id)
    if cluster_delta < 0: # scale down
        for counter in range(cluster_delta,0):
            state = "Starting node decommission for %s" % (cluster_to_scale.cluster_name)
            set_cluster_state(token, cluster_id, state)           
            try:
                node_fqdn, node_id = find_node_to_remove(cluster_to_scale, cyclades, netclient)
                state = "Decommissioning Node %s from %s" % (node_fqdn,cluster_to_scale.cluster_name)
                set_cluster_state(token, cluster_id, state)
                ansible_hosts = modify_ansible_hosts_file(cluster_name_suffix_id, action='remove_slaves',
                                                         slave_hostname=node_fqdn)
                ansible_scale_cluster(ansible_hosts, action='remove_slaves', slave_hostname=node_fqdn.split('.')[0])
            except Exception, e:
                msg = str(e.args[0])
                set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status],
                                  error=msg)
                raise RuntimeError(msg)
            state = "Node %s decommissioned from %s and will be deleted"% (node_fqdn, cluster_to_scale.cluster_name)
            cluster_remove_node(node_fqdn, node_id, token, cluster_id, cluster_to_scale, cyclades,
                                status_map[previous_cluster_status])
    elif cluster_delta > 0: # scale up
        for counter in range(1,cluster_delta+1):
            ret_tuple = check_scale_cluster_up(token, cluster_id, cluster_to_scale)
            # Cannot add any node
            if ret_tuple[1] !=0 and counter == 1:
                msg = ret_tuple[0]
                error_code = ret_tuple[1]
                set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status],
                                  error=msg)
                raise RuntimeError(msg,error_code)
            # Node(s) already added but no more can be added, so the already added will be configured
            elif ret_tuple[1] !=0 and counter > 1:
                break
            # Add node
            try:
                new_slave = cluster_add_node(token, cluster_id, cluster_to_scale, cyclades, netclient, plankton,
                                             status_map[previous_cluster_status])
                list_of_new_slaves.append(new_slave)               
            except Exception, e:
                msg = '{0}. Scale action failed. Cluster rolled back'.format(str(e.args[0]))
                set_cluster_state(token, cluster_id, msg)
                rollback_scale_cluster(list_of_new_slaves, cyclades, cluster_to_scale, pre_scale_size)
                set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status],
                                  error=msg)
                raise RuntimeError(msg)
        state = 'Configuring communication for new nodes of %s ' % cluster_to_scale.cluster_name
        set_cluster_state(token, cluster_id, state)
        master_ip = cluster_to_scale.master_IP
        user_id = new_slave['uuid']
        image_id = new_slave['image_id']
        try:
            for new_slave in list_of_new_slaves:
                reroute_ssh_to_slaves(new_slave['port'], new_slave['private_ip'], master_ip, new_slave['password'], '')
        except Exception, e:
            msg = '{0}. Scale action failed. Cluster rolled back'.format(str(e.args[0]))
            set_cluster_state(token, cluster_id, msg)
            rollback_scale_cluster(list_of_new_slaves, cyclades, cluster_to_scale, pre_scale_size)
            set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status],
                              error=msg)
            raise RuntimeError(msg)
        try:
            ansible_hosts = modify_ansible_hosts_file(cluster_name_suffix_id, list_of_hosts=list_of_new_slaves,
                                                      master_ip=master_ip,
                                                  action='add_slaves')
            state = 'Configuring Hadoop for new nodes of %s ' % cluster_to_scale.cluster_name
            set_cluster_state(token, cluster_id, state)
            ansible_scale_cluster(ansible_hosts, new_slaves_size=len(list_of_new_slaves), orka_image_uuid=image_id,
                                  user_id=user_id)
            modify_ansible_hosts_file(cluster_name_suffix_id, action='join_slaves')  
        except Exception, e:
            msg = '{0}. Scale action failed. Cluster rolled back'.format(str(e.args[0]))
            set_cluster_state(token, cluster_id, msg)
            rollback_scale_cluster(list_of_new_slaves, cyclades, cluster_to_scale, pre_scale_size,ansible=True)
            set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status],
                              error=msg)
            raise RuntimeError(msg)
        finally:
            subprocess.call('rm -rf /tmp/{0}'.format(user_id),shell=True)
    # Restart hadoop cluster for changes to take effect   
    state = "Restarting %s for the changes to take effect" % (cluster_to_scale.cluster_name)
    set_cluster_state(token, cluster_id, state)
    try:
        if REVERSE_HADOOP_STATUS[previous_hadoop_status] == 'stop':
            ansible_manage_cluster(cluster_id, 'start')
        elif REVERSE_HADOOP_STATUS[previous_hadoop_status] == 'start':
            ansible_manage_cluster(cluster_id, 'stop')
            ansible_manage_cluster(cluster_id, 'start')
    
    except Exception, e:
        msg = 'Restarting %s failed with %s. Try to restart it manually.'%(cluster_to_scale.cluster_name,str(e.args[0]))
        set_cluster_state(token, cluster_id, state=msg, status=status_map[previous_cluster_status], error=msg)
        raise RuntimeError(msg)              
    state = 'Scaled cluster %s and new cluster size is %d' %(cluster_to_scale.cluster_name,
                                                             cluster_to_scale.cluster_size)
    set_cluster_state(token, cluster_id, state, status=status_map[previous_cluster_status])
    return cluster_to_scale.cluster_name
        


def destroy_cluster(token, cluster_id, master_IP='', status='Destroyed'):
    """
    Destroys cluster and deletes network and floating IP. Finds the machines
    that belong to the cluster from the cluster id that is given. Cluster id
    is the unique integer that each cluster has in escience database.
    """
    cluster_to_delete = ClusterInfo.objects.get(id=cluster_id)
    cluster_name = cluster_to_delete.cluster_name
    # status is already destroyed or failed, only clean up database 
    if cluster_to_delete.cluster_status not in [const_cluster_status_active,const_cluster_status_pending]:
        current_task.update_state(state="Removing Record")
        try:
            db_cluster_delete(token,cluster_id)
            current_task.update_state(state="Cluster Record Removed")
            return cluster_name
        except Exception,e:
            msg = str(e.args[0])
            raise ClientError(msg, error_cluster_corrupt)
    # cluster exists on cyclades, operate on ~okeanos infrastructure for removal, update database
    current_task.update_state(state="Started")
    servers_to_delete = []
    if cluster_to_delete.master_IP:
        float_ip_to_delete = cluster_to_delete.master_IP
    else:
        float_ip_to_delete = master_IP
    list_of_errors = []
    master_id = None
    network_to_delete_id = None
    float_ip_to_delete_id = None
    new_status = 'placeholder'
    auth = check_credentials(unmask_token(encrypt_key,token))
    current_task.update_state(state="Authenticated")
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], unmask_token(encrypt_key,token))
    nc = init_cyclades_netclient(endpoints['network'], unmask_token(encrypt_key,token))
    # Get list of servers and public IPs
    try:
        list_of_servers = cyclades.list_servers(detail=True)
    except ClientError:
        msg = 'Could not get list of resources.'\
            'Cannot delete cluster'
        raise ClientError(msg, error_get_list_servers)

    # Get master virtual machine and network from IP   
    ip = get_public_ip_id(nc, float_ip_to_delete)
    float_ip_to_delete_id = ip['id']
    master_id = ip['instance_id']          
    master_server = cyclades.get_server_details(master_id)
    for attachment in master_server['attachments']:
         if (attachment['OS-EXT-IPS:type'] == 'fixed' and not attachment['ipv6']):
            network_to_delete_id = attachment['network_id']
            break

    # Show an error message and exit if not valid IP or network
    if not master_id:
        msg = '[%s] is not the valid public IP of the master' % \
            float_ip_to_delete
        raise ClientError(msg, error_get_ip)

    if not network_to_delete_id:
        cyclades.delete_server(master_id)
        set_cluster_state(token, cluster_id, "Deleted master VM", status=status)
        msg = 'A valid network of master and slaves was not found.'\
            'Deleting the master VM only'
        raise ClientError(msg, error_cluster_corrupt)

    # Get the servers of the cluster to be deleted
    for server in list_of_servers:
        for attachment in server['attachments']:
            if attachment['network_id'] == network_to_delete_id:
                servers_to_delete.append(server)
                break
    number_of_nodes = len(servers_to_delete)
    set_cluster_state(token, cluster_id, "Starting deletion of requested cluster")
    # Start cluster deleting
    try:
        for server in servers_to_delete:
            cyclades.delete_server(server['id'])
        state= 'Deleting %d servers ' % number_of_nodes
        set_cluster_state(token, cluster_id, state)
        # Wait for every server of the cluster to be deleted
        for server in servers_to_delete:
            new_status = cyclades.wait_server(server['id'],
                                              current_status='ACTIVE',
                                              max_wait=MAX_WAIT)
            if new_status != 'DELETED':
                logging.error('Error deleting server [%s]' % server['name'])
                list_of_errors.append(error_cluster_corrupt)
        set_cluster_state(token, cluster_id, 'Deleting cluster network and public IP')
    except ClientError:
        logging.exception('Error in deleting server')
        list_of_errors.append(error_cluster_corrupt)

    try:
        nc.delete_network(network_to_delete_id)
        state= 'Network with id [%s] is deleted' % network_to_delete_id
        set_cluster_state(token, cluster_id, state)
        sleep(10)  # Take some time to ensure it is deleted
    except ClientError:
        logging.exception('Error in deleting network')
        list_of_errors.append(error_cluster_corrupt)

    # Delete the floating IP of deleted cluster
    try:
        nc.delete_floatingip(float_ip_to_delete_id)
        state= 'Floating IP [%s] is deleted' % float_ip_to_delete
        logging.log(SUMMARY, state)
        set_cluster_state(token, cluster_id, state)
    except ClientError:
        logging.exception('Error in deleting floating IP [%s]' %
                          float_ip_to_delete)
        list_of_errors.append(error_cluster_corrupt)

    state= 'Cluster with public IP [%s] was deleted ' % float_ip_to_delete
    set_cluster_state(token, cluster_id, state, status=status)
    # Everything deleted as expected
    if not list_of_errors:
        return cluster_name
    # There was one or more errors, return error message
    else:
        msg = 'Error while deleting cluster'
        raise ClientError(msg, list_of_errors[0])


def check_credentials(token, auth_url=auth_url):
    """Identity,Account/Astakos. Test authentication credentials"""
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        msg = ' Authentication failed with url %s and token %s'\
            % (auth_url, token)
        raise ClientError(msg, error_authentication)
    return auth


def get_flavor_lists(token):
    """From kamaki flavor list get all possible flavors """
    auth = check_credentials(token)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    try:
        flavor_list = cyclades.list_flavors(True)
    except ClientError:
        msg = ' Could not get list of flavors'
        raise ClientError(msg, error_flavor_list)
    cpu_list = []
    ram_list = []
    disk_list = []
    disk_template_list = []

    for flavor in flavor_list:
        if flavor['SNF:allow_create']:
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
    return flavors


def get_user_quota(auth):
    """Return user quota"""
    try:
        return auth.get_quotas()
    except ClientError:
        msg = ' Could not get user quota'
        raise ClientError(msg, error_user_quota)


def check_quota(token, project_id):
    """
    Checks if user available quota .
    Available = limit minus (~ okeanos used and escience pending).
    Also divides with 1024*1024*1024 to transform bytes to gigabytes.
    """
    auth = check_credentials(token)
    dict_quotas = get_user_quota(auth)
    project_name = auth.get_project(project_id)['name']
    endpoints, user_id = endpoints_and_user_id(auth)
    net_client = init_cyclades_netclient(endpoints['network'],token)
    # Get pending quota for given project id
    pending_quota = retrieve_pending_clusters(token, project_name)
    # Quotas are allocated per project and per user account. 
    # So some  other account in the same project may have bind some of user quota since project_quota maybe be different than number_of_users*user_quota
    # The result is user limit quota might be less than it seems so we have to consider project limit as well
    
    limit_cd = dict_quotas[project_id]['cyclades.disk']['limit'] / Bytes_to_GiB # Convert bytes to GiB, 1 GiB = 1024*1024*1024  bytes 
    usage_cd = dict_quotas[project_id]['cyclades.disk']['usage'] / Bytes_to_GiB
    project_limit_cd = dict_quotas[project_id]['cyclades.disk']['project_limit'] / Bytes_to_GiB
    project_usage_cd = dict_quotas[project_id]['cyclades.disk']['project_usage'] / Bytes_to_GiB
    pending_cd = pending_quota['Disk']
    available_cyclades_disk_GB = limit_cd-usage_cd
    if (available_cyclades_disk_GB > (project_limit_cd - project_usage_cd)):
        available_cyclades_disk_GB = project_limit_cd - project_usage_cd
    available_cyclades_disk_GB = available_cyclades_disk_GB - pending_cd

    limit_cpu = dict_quotas[project_id]['cyclades.cpu']['limit']
    usage_cpu = dict_quotas[project_id]['cyclades.cpu']['usage']
    project_limit_cpu = dict_quotas[project_id]['cyclades.cpu']['project_limit']
    project_usage_cpu = dict_quotas[project_id]['cyclades.cpu']['project_usage']
    pending_cpu = pending_quota['Cpus']
    available_cpu = limit_cpu - usage_cpu
    if (available_cpu > (project_limit_cpu - project_usage_cpu)):
        available_cpu = project_limit_cpu - project_usage_cpu
    available_cpu = available_cpu - pending_cpu

    limit_ram = dict_quotas[project_id]['cyclades.ram']['limit'] / Bytes_to_MiB # Convert bytes to MiB, 1 MiB = 1024*1024 bytes 
    usage_ram = dict_quotas[project_id]['cyclades.ram']['usage'] / Bytes_to_MiB
    project_limit_ram = dict_quotas[project_id]['cyclades.ram']['project_limit'] / Bytes_to_MiB
    project_usage_ram = dict_quotas[project_id]['cyclades.ram']['project_usage'] / Bytes_to_MiB
    pending_ram = pending_quota['Ram']
    available_ram = limit_ram-usage_ram
    if (available_ram > (project_limit_ram - project_usage_ram)):
        available_ram = project_limit_ram - project_usage_ram
    available_ram = available_ram - pending_ram

    limit_vm = dict_quotas[project_id]['cyclades.vm']['limit']
    usage_vm = dict_quotas[project_id]['cyclades.vm']['usage']
    project_limit_vm = dict_quotas[project_id]['cyclades.vm']['project_limit']
    project_usage_vm = dict_quotas[project_id]['cyclades.vm']['project_usage']
    pending_vm = pending_quota['VMs']
    available_vm = limit_vm-usage_vm
    if (available_vm > (project_limit_vm - project_usage_vm)):
        available_vm = project_limit_vm - project_usage_vm
    available_vm = available_vm - pending_vm
    
    pending_net = pending_quota['Network']
    limit_net = dict_quotas[project_id]['cyclades.network.private']['limit']
    usage_net = dict_quotas[project_id]['cyclades.network.private']['usage']
    project_limit_net = dict_quotas[project_id]['cyclades.network.private']['project_limit']
    project_usage_net = dict_quotas[project_id]['cyclades.network.private']['project_usage']
    available_networks = limit_net - usage_net
    if (available_networks > (project_limit_net - project_usage_net)):
        available_networks = project_limit_net - project_usage_net
    available_networks -= pending_net
    
    list_float_ips = net_client.list_floatingips()
    pending_ips = pending_quota['Ip']
    limit_ips = dict_quotas[project_id]['cyclades.floating_ip']['limit']
    usage_ips = dict_quotas[project_id]['cyclades.floating_ip']['usage']
    project_limit_ips = dict_quotas[project_id]['cyclades.floating_ip']['project_limit']
    project_usage_ips = dict_quotas[project_id]['cyclades.floating_ip']['project_usage']
    available_ips = limit_ips-usage_ips
    if (available_ips > (project_limit_ips - project_usage_ips)):
        available_ips = project_limit_ips - project_usage_ips
    available_ips -= pending_ips
    for d in list_float_ips:
        if d['instance_id'] is None and d['port_id'] is None:
            available_ips += 1

    quotas = {'cpus': {'limit': limit_cpu, 'available': available_cpu},
              'ram': {'limit': limit_ram, 'available': available_ram},
              'disk': {'limit': limit_cd, 'available': available_cyclades_disk_GB},
              'cluster_size': {'limit': limit_vm, 'available': available_vm},
              'network': {'available': available_networks},
              'float_ips': {'available': available_ips}}
    return quotas


def check_images(token, project_id):
    """
    Checks the list of the current images
    Filter the ones that match with our uuid
    Return the available images
    """
    auth = check_credentials(token)
    endpoints, user_id = endpoints_and_user_id(auth)    
    plankton = init_plankton(endpoints['plankton'], token)
    list_current_images = plankton.list_public(True, 'default')
    vre_images_in_db = VreImage.objects.values('image_pithos_uuid')
    orka_images_in_db = OrkaImage.objects.values('image_pithos_uuid')
    available_images = []
    hadoop_images = []
    vre_images = []
    for image in list_current_images:
        if any(d['image_pithos_uuid'] == image['id'] for d in vre_images_in_db):
            vre_images.append(image['name'])
        if any(d['image_pithos_uuid'] == image['id'] for d in orka_images_in_db):         
            hadoop_images.append(image['name'])
    # hadoop images at ordinal 0, vre images at 1
    available_images.append(hadoop_images)
    available_images.append(vre_images)        
    return available_images

def endpoints_and_user_id(auth):
    """
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    """
    logging.log(REPORT, ' Get the endpoints')
    try:
        endpoints = dict(
            astakos=auth.get_service_endpoints('identity')['publicURL'],
            cyclades=auth.get_service_endpoints('compute')['publicURL'],
            pithos=auth.get_service_endpoints('object-store')['publicURL'],
            plankton=auth.get_service_endpoints('image')['publicURL'],
            network=auth.get_service_endpoints('network')['publicURL']
            )
        user_id = auth.user_info['id']
    except ClientError:
        msg = ' Failed to get endpoints & user_id from identity server'
        raise ClientError(msg)
    return endpoints, user_id


def init_cyclades_netclient(endpoint, token):
    """
    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating IP
    """
    logging.log(REPORT, ' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades network client'
        raise ClientError(msg)


def init_plankton(endpoint, token):
    """
    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    """
    logging.log(REPORT, ' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize the Image client'
        raise ClientError(msg)


def init_cyclades(endpoint, token):
    """
    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    """
    logging.log(REPORT, ' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades client'
        raise ClientError(msg)


def get_float_network_id(cyclades_network_client, project_id):
        """
        Gets an Ipv4 floating network id from the list of public networks Ipv4
        """
        pub_net_list = cyclades_network_client.list_networks()
        float_net_id = 1
        i = 1
        for lst in pub_net_list:
            if(lst['status'] == 'ACTIVE' and
               lst['name'] == 'Public IPv4 Network'):
                float_net_id = lst['id']
                try:
                    cyclades_network_client.create_floatingip(float_net_id, project_id=project_id)
                    return 0
                except ClientError:
                    if i < len(pub_net_list):
                        i = i+1
        return error_get_ip
    
def personality(ssh_keys_path='', pub_keys_path='', vre_script_path=''):
        """Personality injects ssh keys to the virtual machines we create"""
        personality = []
        if vre_script_path:
            try:
                with open(abspath(vre_script_path)) as vre_script:
                    personality.append(dict(
                        contents=b64encode(vre_script.read()),
                        path='/root/{0}'.format(basename(vre_script.name)),
                        owner='root'))
            except IOError:
                msg = " No valid VRE shell script in %s" %((abspath(vre_script_path)))
                raise IOError(msg)
        if ssh_keys_path and pub_keys_path:
            try:
                with open(abspath(ssh_keys_path)) as f1, open(abspath(pub_keys_path)) as f2:
                    personality.append(dict(
                        contents=b64encode(f1.read() + f2.read()),
                        path='/root/.ssh/authorized_keys',
                        owner='root', group='root', mode=0600))
            except IOError:
                msg = " No valid public ssh key(id_rsa.pub) in %s or %s" %((abspath(ssh_keys_path)),(abspath(pub_keys_path)))
                raise IOError(msg)
        elif ssh_keys_path or pub_keys_path:
            try:
                keys_path = ssh_keys_path if ssh_keys_path else pub_keys_path
                with open(abspath(keys_path)) as f:
                    personality.append(dict(
                        contents=b64encode(f.read()),
                        path='/root/.ssh/authorized_keys',
                        owner='root', group='root', mode=0600))
            except IOError:
                msg = " No valid public ssh key(id_rsa.pub) in " + (abspath(keys_path))
                raise IOError(msg)
        if ssh_keys_path or pub_keys_path:
                personality.append(dict(
                    contents=b64encode('StrictHostKeyChecking no'),
                    path='/root/.ssh/config',
                    owner='root', group='root', mode=0600))
        return personality


class Cluster(object):
    """
    Cluster class represents an entire ~okeanos cluster.Instantiation of
    cluster gets the following arguments: A CycladesClient object,a name-prefix
    for the cluster,the flavors of master and slave machines,the image id of
    their OS, the size of the cluster,a CycladesNetworkClient object, an
    AstakosClient object and the project_id.
    """
    def __init__(self, cyclades, prefix, flavor_id_master, flavor_id_slave,
                 image_id, size, net_client, auth_cl, project_id):
        self.client = cyclades
        self.nc = net_client
        self.prefix, self.size = prefix, int(size)
        self.flavor_id_master, self.auth = flavor_id_master, auth_cl
        self.flavor_id_slave, self.image_id = flavor_id_slave, image_id
        self.project_id = project_id

    def clean_up(self, servers=None, network=None):
        """Delete resources after a failed attempt to create a cluster"""
        if not (network and servers):
            logging.error(' Nothing to delete')
            return
        logging.error(' An unrecoverable error occured in ~okeanos.'
                      'Cleaning up and shutting down')
        status = ''
        if servers:
            for server in servers:
                status = self.client.get_server_details(server['id'])['status']
                if status == 'BUILD':
                    status = self.client.wait_server(server['id'],
                                                     max_wait=MAX_WAIT)
                self.client.delete_server(server['id'])

                new_status = self.client.wait_server(server['id'],
                                                     current_status=status,
                                                     max_wait=MAX_WAIT)
                logging.log(REPORT, ' Server [%s] is being %s', server['name'],
                            new_status)
                if new_status != 'DELETED':
                    logging.error(' Error deleting server [%s]' % server['name'])
        if network:
            self.nc.delete_network(network['id'])

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        """
        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        """
        logging.log(REPORT, ' Create %s servers prefixed as [%s]',
                    self.size, self.prefix)
        servers = []
        empty_ip_list = []
        list_of_ports = []
        count = 0
        hostname_master = ''
        i = 0
        port_status = ''
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s' % (self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = self.prefix
        # Creates network
        try:
            new_network = self.nc.create_network('MAC_FILTERED', net_name,
                                                 project_id=self.project_id)
        except ClientError:
            msg = ' Error in creating network'
            raise ClientError(msg, error_create_network)

        # Gets list of floating ips
        try:
            list_float_ips = self.nc.list_floatingips()
        except ClientError:
            self.clean_up(network=new_network)
            msg = ' Error getting list of floating ips'
            raise ClientError(msg, error_get_ip)
        # If there are existing floating ips,we check if there is any free or
        # if all of them are attached to a machine
        if len(list_float_ips) != 0:
            for float_ip in list_float_ips:
                if float_ip['instance_id'] is None and float_ip['port_id'] is None:
                    break
                else:
                    count = count+1
                    if count == len(list_float_ips):
                        try:
                            self.nc.create_floatingip(list_float_ips
                                                      [count-1]
                                                      ['floating_network_id'],
                                                      project_id=self.project_id)
                        except ClientError:
                            if get_float_network_id(self.nc, project_id=self.project_id) != 0:
                                self.clean_up(network=new_network)
                                msg = ' Error in creating float IP'
                                raise ClientError(msg, error_get_ip)
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            if get_float_network_id(self.nc, project_id=self.project_id) != 0:
                self.clean_up(network=new_network)
                msg = ' Error in creating float IP'
                raise ClientError(msg, error_get_ip)
        logging.log(REPORT, ' Wait for %s servers to build', self.size)

        # Creation of master server

        try:
            servers.append(self.client.create_server(
                server_name, self.flavor_id_master, self.image_id,
                personality=personality(ssh_k_path, pub_k_path),
                project_id=self.project_id))
        except ClientError:
            self.clean_up(servers=servers, network=new_network)
            msg = ' Error creating master VM [%s]' % server_name
            raise ClientError(msg, error_create_server)
        # Creation of slave servers
        for i in range(2, self.size+1):
            try:

                server_name = '%s%s%s' % (self.prefix, '-', i)
                servers.append(self.client.create_server(
                    server_name, self.flavor_id_slave, self.image_id,
                    personality=personality(ssh_k_path, pub_k_path),
                    networks=empty_ip_list, project_id=self.project_id))

            except ClientError:
                self.clean_up(servers=servers, network=new_network)
                msg = ' Error creating server [%s]' % server_name
                raise ClientError(msg, error_create_server)
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        try:
            new_status = self.client.wait_server(servers[0]['id'],
                                                 max_wait=MAX_WAIT)
            if new_status != 'ACTIVE':
                msg = ' Status for server [%s] is %s' % \
                    (servers[i]['name'], new_status)
                raise ClientError(msg, error_create_server)
            logging.log(REPORT, ' Status for server [%s] is %s',
                        servers[0]['name'], new_status)
            # Create a subnet for the virtual network between master
            #  and slaves along with the ports needed
            self.nc.create_subnet(new_network['id'], '192.168.0.0/24',
                                  enable_dhcp=True)
            port_details = self.nc.create_port(new_network['id'],
                                               servers[0]['id'])
            port_status = self.nc.wait_port(port_details['id'],
                                            max_wait=MAX_WAIT)
            if port_status != 'ACTIVE':
                msg = ' Status for port [%s] is %s' % \
                    (port_details['id'], port_status)
                raise ClientError(msg, error_create_server)
            # Wait server for the slaves, so we can use their server id
            # in port creation
            for i in range(1, self.size):
                new_status = self.client.wait_server(servers[i]['id'],
                                                     max_wait=MAX_WAIT)
                if new_status != 'ACTIVE':
                    msg = ' Status for server [%s] is %s' % \
                        (servers[i]['name'], new_status)
                    raise ClientError(msg, error_create_server)
                logging.log(REPORT, ' Status for server [%s] is %s',
                            servers[i]['name'], new_status)
                port_details = self.nc.create_port(new_network['id'],
                                                   servers[i]['id'])
                list_of_ports.append(port_details)

            for port in list_of_ports:
                port_status = self.nc.get_port_details(port['id'])['status']
                if port_status == 'BUILD':
                    port_status = self.nc.wait_port(port['id'],
                                                    max_wait=MAX_WAIT)
                if port_status != 'ACTIVE':
                    msg = ' Status for port [%s] is %s' % \
                        (port['id'], port_status)
                    raise ClientError(msg, error_create_server)
        except Exception:
            self.clean_up(servers=servers, network=new_network)
            raise

        if server_log_path:
            logging.info(' Store passwords in file [%s]', server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)

        # hostname_master is always the public IP of master node
        master_details = self.client.get_server_details(servers[0]['id'])
        for attachment in master_details['attachments']:
            if attachment['OS-EXT-IPS:type'] == 'floating':
                        hostname_master = attachment['ipv4']
        return hostname_master, servers


def read_replication_factor(document):
    """
    Returns default replication factor from Hadoop xml config file.
    """
    root = document.getroot()
    for child in root.iter("property"):
        name = child.find("name").text
        if name == "dfs.replication":
            replication_factor = int(child.find("value").text)
            break
    return replication_factor


def get_remote_server_file_size(url, user='', password=''):
    """
    Returns the file size of a given remote server.
    First it recreates the remote server url with the username and password
    given or empty if not given. Then does a HEAD request for the
    content-length header which is the file size in bytes.
    """
    url_in_list = url.split("://", 1)
    url_in_list.insert(1, "://" + user + ':' + password + '@')
    new_url = ''.join(url_in_list) # creates url for curl command
    r = subprocess.call("curl -sI " + new_url +
                                " | grep -i content-length | awk \'{print $2}\' | tr -d '\r\n'", shell=True)
    return int(r)