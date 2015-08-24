#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the definitions of returned errors and package constants.

@author: Ioannis Stenos, Nick Vrionis
"""
import os

# Definitions of return value success and errors
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
error_quotas_cluster_size = -13
error_quotas_network = -14
error_flavor_id = -15
error_image_id = -16
error_syntax_token = -17
error_ready_reroute = -18
error_no_arguments = -19
error_fatal = -20
error_user_quota = -22
error_flavor_list = -23
error_get_list_servers = -24
error_get_list_projects = -25
error_get_network_quota = -28
error_create_network = -29
error_get_ip = -30
error_create_server = -31
error_syntax_auth_token = -32
error_ansible_playbook = -34
error_ssh_client = -35
error_cluster_not_exist = -69
error_cluster_corrupt = -70
error_proj_id = -71
error_multiple_entries = -72
error_project_quota = -73
error_authentication = -99
error_replication_factor = -36
SUCCESS = 0

# Package constants
REPORT = 25  # Define logging level of REPORT
SUMMARY = 29  # Define logging level of SUMMARY
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
default_image = 'Debian Base'
images_without_hue = ['Debian Base', 'Hadoop-2.5.2']
default_logging = 'summary'
login_endpoint = '/api/users'
cluster_endpoint = '/api/clusterchoices'
job_endpoint = '/api/jobs'
hdfs_endpoint = '/api/hdfs'
vre_endpoint = '/api/vreservers'
vre_images_endpoint = '/api/vreimages'
orka_images_endpoint = '/api/orkaimages'
node_endpoint = '/api/nodeservers'
wait_timer_create = 30
wait_timer_delete = 5
const_cluster_status_destroyed = "0"
const_cluster_status_active = "1"
const_cluster_status_pending = "2"
const_cluster_status_failed = "3"
const_hadoop_status_started = "1"
const_hadoop_status_stopped = "0"
const_escience_uuid = "ec567bea-4fa2-433d-9935-261a0867ec60"
HADOOP_PATH = '/usr/local/hadoop/bin/hdfs'
DEFAULT_HDFS_DIR = ['/user/hduser', '/user/hduser/']
FNULL = open(os.devnull, 'w')
block_size = 67108864 # block size in bytes,used in division when transfering files from hdfs to pithos
# Dictionaries with constants used in images list
ORKA_IMAGES = {'action':'orka_images','resource_name':'orkaimage'}
VRE_IMAGES = {'action':'vre_images','resource_name':'vreimage'}