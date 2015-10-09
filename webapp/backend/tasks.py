#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains the celery tasks that will be executed from django views.

@author: e-science Dev-team
"""
from celery.task import task
from create_cluster import YarnCluster
from okeanos_utils import destroy_cluster, destroy_server, scale_cluster, create_dsl, destroy_dsl
from run_ansible_playbooks import ansible_manage_cluster
from reroute_ssh import HdfsRequest


@task()
def create_cluster_async(choices):
    """
    Asynchronous create cluster task.
    """
    new_yarn_cluster = YarnCluster(choices)
    MASTER_IP, servers, password, cluster_id = new_yarn_cluster.create_yarn_cluster()
    task_result = {"master_IP": MASTER_IP, "master_VM_password": password, "cluster_id": cluster_id}

    return task_result

@task()
def scale_cluster_async(token, cluster_id, cluster_delta):
    """
    Asynchronous scale cluster task.
    """
    result = scale_cluster(token, cluster_id, cluster_delta)
    return result

@task()
def destroy_cluster_async(token, cluster_id):
    """
    Asynchronous destroy cluster task.
    """
    result = destroy_cluster(token, cluster_id)
    return result


@task()
def hadoop_cluster_action_async(cluster_id, action):
    """
    Asynchronous start, stop or format Hadoop cluster task.
    """
    result = ansible_manage_cluster(cluster_id, action)
    return result


@task()
def put_hdfs_async(opts):
    """
    Asynchronous task to put a file in hdfs.
    """
    put_file_request = HdfsRequest(opts)
    result = put_file_request.put_file_hdfs()
    return result

@task()
def create_server_async(choices):
    """
    Asynchronous create VRE server task.
    """
    new_vre_server = YarnCluster(choices)
    server_id, server_pass, server_ip = new_vre_server.create_vre_server()
    task_result = {"server_IP": server_ip, "VRE_VM_password": server_pass, "server_id": server_id}
    return task_result

@task()
def destroy_server_async(token, id):
    """
    Asynchronous destroy VRE server task.
    """
    result = destroy_server(token, id)
    return result

@task()
def create_dsl_async(choices):
    """
    Asynchronous create Cluster DSL task.
    """
    new_dsl_id, pithos_path, dsl_name = create_dsl(choices)
    task_result = {"dsl_name": dsl_name, "pithos_path": pithos_path, "dsl_id": new_dsl_id}
    return task_result

@task()
def destroy_dsl_async(token, id):
    """
    Asynchronous destroy DSL task.
    """
    result = destroy_dsl(token, id)
    return result    