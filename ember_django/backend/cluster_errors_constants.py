#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the definitions of returned errors and package constants.

@author: Ioannis Stenos, Nick Vrionis
"""

# Definitions of return value errors
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

# Package constants
ADD_TO_GET_PORT = 9998  # Value to add in order to get slave port numbers
REPORT = 25  # Define logging level of REPORT
SUMMARY = 29  # Define logging level of SUMMARY
Mbytes_to_GB = 1024  # Global to convert megabytes to gigabytes
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
storage_template = {'ext_vlmc':'Archipelago','drbd':'Standard'} # ~okeanos available storage templates with user friendly name
reverse_storage_template = {'Archipelago':'ext_vlmc','Standard':'drbd'} # ~okeanos available storage templates with user friendly name
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
default_image = 'Debian Base'
default_logging = 'summary'
login_endpoint = '/api/users'
cluster_endpoint = '/api/clusterchoices'
job_endpoint = '/api/jobs'
HADOOP_STATUS_ACTIONS = {"stop": ["0","Stopping","stopped"],
                         "start": ["1","Starting","started"],
                         "format": ["2","Formatting","formatted"],
                         "makehduser": ["3", "Creating /user/hduser in HDFS", "Created /user/hduser"]}

REVERSE_HADOOP_STATUS = {"0":"stop", "1":"start", "2":"Pending"}