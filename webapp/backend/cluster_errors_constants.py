#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the definitions of returned errors and package constants.

@author: e-science Dev-team
"""
import os
import base64
from os.path import join, abspath, dirname
# Definitions of return value errors


error_quotas_cyclades_disk = -10 	# Not enough disksize quota in cyclades 
error_quotas_cpu = -11 			# Not enough cpu quota in cyclades 
error_quotas_ram = -12 			# Not enough ram quota in cyclades
error_quotas_cluster_size = -13 	# Not enough VM quota in cyclades
error_quotas_network = -14 		# Not enough private network quota 
error_flavor_id = -15 			# Not a valid combination of resources
error_image_id = -16 			# Not a valid image given
error_fatal = -20 			# Often used in orka cli for many errors(ClientError,ConnectionError), only once in backend(deletion error in delete vre)
error_user_quota = -22 			# Error requesting/getting user quota from ~okeanos
error_flavor_list = -23 		# Error requesting/getting flavors list from ~okeanos
error_get_list_servers = -24 		# Error requesting/getting user's servers from ~okeanos
error_get_list_projects = -25 		# Error requesting/getting user's projects from ~okeanos
error_create_network = -29 		# Error creating private network in ~okeanos
error_get_ip = -30  			# General floating IP error (e.g. not enough ip quota and error while requesting list of ips)
error_create_server = -31 		# Error while creating ~okeanos server (e.g. stay in BUILD status more than 5 minutes).
error_ansible_playbook = -34 		# General error while running create cluster Ansible playbook
error_ssh_client = -35 			# Error for staging server not be able to connect to cluster during reroute steps
error_cluster_corrupt = -70 		# Error while deleting cluster and not all VMs are deleted(e.g. Error before deleting all cluster VMs)
error_project_id = -71	 		# No project id for given project name
error_multiple_entries = -72 		# Multiple entries in database for something unique
error_project_quota = -73 		# Zero user quota for a given project       
error_authentication = -99 		# Invalid token
error_container = -76 			# Error pithos container not found while upload dsl file
error_import_dsl = -78 			# Failed to import DSL file from pithos
error_pithos_connection = -79 		# Failed to reach Pithos filesystem

FNULL = open(os.devnull, 'w') 		# Redirects whatever is assigned to FNULL to nothingness (e.g. stderr=FNULL)

DEFAULT_HADOOP_USER ='hduser' 		# Default system user account running hadoop 
DEFAULT_HADOOP_CONF_VALUES = {'dfs_blocksize': '128', 'replication_factor': 2}

# Hadoop test command error return status
error_hdfs_test_exit_status = 1 	# 1 is error exit status returned from hadoop test commands (e.g. hadoop fs -test -e <some_path> )

# Package constants
ADD_TO_GET_PORT = 9998  		# Value offset in order to get slave port numbers, STARTING FROM?...
REPORT = 31             		# Define logging level of REPORT
SUMMARY = 32            		# Define logging level of SUMMARY
MAX_WAIT = 300          		# Max number of seconds for wait function of Cyclades
UUID_FILE = 'permitted_uuids.txt'	# File of ~okeanos uuid's allowed to login
FILES_DIR = join(dirname(abspath(__file__)), "files") # Location of files directory. This is where files that will be copied to a Hadoop cluster without using ansible playbooks are stored.
LOGS_PATH = join(os.path.expanduser('~'),"logs")# Location of personal orka server and ansible log files
# MiB <-> GiB easy conversion constants
Mbytes_to_GB = 1024     	# Global to convert megabytes to gigabytes
Bytes_to_MiB = 1048576   	# Global to convert bytes to megabytes
Bytes_to_GiB = 1073741824  	# Global to convert bytes to gigabytes

# Used for storage template conversion in get_flavors_quotas, so user-friendly args can be used in cli and gui
storage_template = {'ext_vlmc':'Archipelago','drbd':'Standard'} # ~okeanos available storage templates with friendly name

# Default ~okeanos endpoints and responses
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
pithos_url = 'https://pithos.okeanos.grnet.gr/v1'
pithos_put_success = 201  		# Success pithos response
pithos_container_not_found = 404
pithos_object_not_found = pithos_container_not_found

# Cluster status constants
const_cluster_status_destroyed = "0"
const_cluster_status_active = "1"
const_cluster_status_pending = "2"
const_cluster_status_failed = "3"
# Hadoop status constants
const_hadoop_status_stopped = "0"
const_hadoop_status_started = "1"
const_hadoop_status_format = "2"
const_hadoop_status_undefined = "3"
# Experiment status constants
const_experiment_status_atrest = "0"
const_experiment_status_replay = "1"

# Set Hadoop pending status to 2 (same as Hadoop status format and cluster status pending)
const_hadoop_status_pending = const_hadoop_status_format

# If celery message is bigger than following value, it truncates the message. If message length > const_truncate_limit, then add dots (..) at the end of message to indicate truncation. Used for orka cli mainly.
const_truncate_limit = 350

# Hadoop cluster status and messages
HADOOP_STATUS_ACTIONS = {"stop": ["0", "Stopping", "Stopped"],
                         "start": ["1", "Starting", "Started"],
                         "format": ["2", "Formatting", "Formatted"],
                         "undefined": ["3", "Undefined", "Undefined"]}
REVERSE_HADOOP_STATUS = {v[0]: k for k, v in HADOOP_STATUS_ACTIONS.items()}
REVERSE_HADOOP_STATUS["2"] = "Pending"
REVERSE_HADOOP_STATUS["3"] = "Undefined"

