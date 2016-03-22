#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains useful classes and fuctions for orka replay.

@author: e-science Dev-team
"""

import re
import subprocess
import yaml
import urllib
import requests
from urllib2 import urlopen, Request, HTTPError
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
from backend.models import UserInfo, ClusterInfo, VreServer, Dsl, OrkaImage, VreImage
from django_db_after_login import get_user_id
from django_db_after_login import db_cluster_update, db_cluster_delete, get_user_id, db_server_update, db_hadoop_update, db_dsl_create, db_dsl_update, db_dsl_delete

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
    cluster_options.setdefault('dfs_blocksize', DEFAULT_HADOOP_CONF_VALUES['dfs_blocksize'])
    replication_factor_default = str(min(int(cluster_options['cluster_size'])-1, DEFAULT_HADOOP_CONF_VALUES['replication_factor']))
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
    sleep(6)

def action_stop(token, dsl_id, task, msg):
    """
    Replay experiment helper function.
    Wrap task and db update for failure in an easy call.
    """
    task.update_state(state=msg)
    db_dsl_update(token,dsl_id,dsl_status=const_experiment_status_atrest,state=msg,error=msg)
    sleep(6)

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
    
