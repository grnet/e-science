#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the definitions of returned errors and package constants.

@author: e-science Dev-team
"""
import os

# Definitions of return value success and errors
error_no_arguments = -19
error_fatal = -20
error_syntax_auth_token = -32
error_replication_factor = -36
error_remove_node = -37
error_authentication = -99
SUCCESS = 0

# Package constants
REPORT = 25  # Define logging level of REPORT
SUMMARY = 29  # Define logging level of SUMMARY
DEFAULT_SSL_VALUE = False
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
pithos_url = 'https://pithos.okeanos.grnet.gr/v1'
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
wait_timer_create = 30
wait_timer_delete = 5
const_cluster_status_destroyed = "0"
const_cluster_status_active = "1"
const_cluster_status_pending = "2"
const_cluster_status_failed = "3"
const_hadoop_status_started = "1"
const_hadoop_status_stopped = "0"
HADOOP_PATH = '/usr/local/hadoop/bin/hdfs'
DEFAULT_HDFS_DIR = ['/user/hduser', '/user/hduser/']
DEFAULT_HADOOP_USER ='hduser'
FNULL = open(os.devnull, 'w')
block_size = 67108864 # block size in bytes,used in division when transfering files from hdfs to pithos
# Dictionaries with constants used in images list
ORKA_IMAGES = {'action':'orka_images','resource_name':'orkaimage'}
VRE_IMAGES = {'action':'vre_images','resource_name':'vreimage'}
vre_ram_min = 1024
dspace_bbb_ram_min = 2048
bbb_cpu_min = 2
REPLAY_ACTIONS_PREFIX = 'REPLAY'
