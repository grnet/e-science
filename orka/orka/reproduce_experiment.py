#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reproduces the experiment that is stored in a yaml file
"""

import os, sys
import yaml
import subprocess
import requests
from cluster_errors_constants import *
from utils import get_file_protocol, get_user_id
FNULL = open(os.devnull, 'w')

def create_cluster(script):

    # create the appropriate command based on the given info
    create_cluster_command = ("orka create")
    
    if script["cluster"].get("name") is not None:
        create_cluster_command += (" " + script["cluster"]["name"])

    if script["cluster"].get("size") is not None:
        create_cluster_command += (" " + str(script["cluster"]["size"]))  

    if script["cluster"].get("flavor_master") is not None:
        create_cluster_command += (" " + str(script["cluster"].get("flavor_master")[0]))
        create_cluster_command += (" " + str(script["cluster"].get("flavor_master")[1]))
        create_cluster_command += (" " + str(script["cluster"].get("flavor_master")[2]))

    if script["cluster"].get("flavor_slaves") is not None:
        create_cluster_command += (" " + str(script["cluster"].get("flavor_slaves")[0]))
        create_cluster_command += (" " + str(script["cluster"].get("flavor_slaves")[1]))
        create_cluster_command += (" " + str(script["cluster"].get("flavor_slaves")[2]))

    if script["cluster"].get("disk_template") is not None:
        if script["cluster"]["disk_template"] == 'drbd':
            create_cluster_command += (" Standard")
        if script["cluster"]["disk_template"] == 'ext_vlmc':
            create_cluster_command += (" Archipelago")

    if script["cluster"].get("project_name") is not None:
        create_cluster_command += (" " + script["cluster"]["project_name"])        

    if script["cluster"].get("image") is not None:
        create_cluster_command += (" --image=" + script["cluster"]["image"])

    if script["cluster"].get("personality") is not None:
        create_cluster_command += (" --personality=" + script["cluster"]["personality"])

    if script.get("configuration") is not None:
        if script["configuration"].get("replication_factor") is not None:
            create_cluster_command += (" --replication_factor=" 
                                   + str(script["configuration"]["replication_factor"]))
        if script["configuration"].get("dfs_blocksize") is not None:
            create_cluster_command += (" --dfs_blocksize=" 
                                   + str(script["configuration"]["dfs_blocksize"]))

    # temp file to store cluster details
    tempfile = "_" + script["cluster"]["name"] + ".txt"
    create_cluster_command += (" | tee " + tempfile)
 
    # create cluster
    print '--- Creating Cluster ---'
    exit_status = os.system(create_cluster_command)
    if exit_status != 0:
        print 'Cluster (re-)creation failed with exit status %d' % exit_status
        sys.exit(0)

    print ''
    # retrieve cluster id and master IP
    with open(tempfile, 'r') as f:
        cluster_id = f.readline().strip().split(': ')[1]    
        master_IP = f.readline().strip().split(': ')[1]

    # remove temp file
    os.remove(tempfile)
    
    return cluster_id, master_IP

def enforce_actions(script, cluster_id, master_IP):

    print '--- Executing Actions ---'
    # Enforce actions
    for action in script["actions"]:
        if action in ["start", "stop", "format"]:
            print ("- Action: Hadoop " + action)
            os.system("orka hadoop " + action + " " + str(cluster_id))
            print ''
        if action.startswith("put"):
            params_string = action.strip('put')
            params = params_string.strip(' ()')
            action_params = params.split(',')
            print ("- Action: Uploading file to hdfs")
            os.system("orka file put " + str(cluster_id) + " " + action_params[0] + " " + action_params[1])
            print ''
        if action.startswith("get"):
            params_string = action.strip('get')
            params = params_string.strip(' ()')
            action_params = params.split(',')
            print ("- Action: Retrieving file from hdfs")
            os.system("orka file get " + str(cluster_id) + " " + action_params[0] + " " + action_params[1])
            print ''
        if action == 'node_add':
            print ("- Action: Adding node to hadoop")
            os.system("orka node add " + str(cluster_id))
            print ''
        if action == 'node_remove':
            print ("- Action: Removing node from hadoop")
            os.system("orka node remove " + str(cluster_id))
            print ''
        if action.startswith("run_job"):
            run_job(action, master_IP)
            
def run_job(action, master_IP):

    # retrieve user and job
    params_string = action.strip('run_job')
    params = params_string.strip(' ()')
    action_params = params.split(',')
    user = action_params[0]
    job = action_params[1].strip('\" ')
    
    print ("- Action: Running job")
    response = subprocess.call( "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " 
                                + user + "@" + master_IP + " \'" 
                                + job + "\'"
                                , stderr=FNULL, shell=True)
    print ''

def replay(argv, token):
    
    # get user's uuid
    uuid = get_user_id(token)
    
    # check files's protocol
    file_protocol, remain = get_file_protocol(argv, 'fileput', 'source')

    if file_protocol == 'pithos':
        url = pithos_url + "/" + uuid + remain
        headers = {'X-Auth-Token':'{0}'.format(token)}
        r=requests.get(url, headers=headers)
        # load the experiment from pithos file
        script = yaml.load(r.text)
    else:
        # load the experiment from local file
        with open(argv, 'r') as f:
            script = yaml.load(f)

    # check if cluster info is given (cluster info is mandatory)
    if script.get("cluster") is None:
        print "Cluster information is missing."
        return
    
    print '--- Reproducing Experiment ---'
    # check if the cluster will be created (no cluster id is given)
    # find the correct cluster id / master IP to be used later for actions
    if script["cluster"].get("cluster_id") is None:
        cluster_id, master_IP = create_cluster(script)
    else:
        cluster_id = script["cluster"].get("cluster_id")
        master_IP = script["cluster"].get("master_IP")

    # proceed with the list of actions
    if script.get("actions") is not None:
        enforce_actions(script, cluster_id, master_IP)
