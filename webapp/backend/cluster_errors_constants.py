#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the definitions of returned errors and package constants.

@author: Ioannis Stenos, Nick Vrionis
"""
import os
import base64
from encrypt_key import key #file with only one variable key = encrypt_key file is not in git repo
encrypt_key = key

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
FNULL = open(os.devnull, 'w')
# Hadoop test command error return status
error_hdfs_test_exit_status = 1

# Package constants
ADD_TO_GET_PORT = 9998  # Value to add in order to get slave port numbers
REPORT = 25  # Define logging level of REPORT
SUMMARY = 29  # Define logging level of SUMMARY
MAX_WAIT = 300  # Max number of seconds for wait function of Cyclades
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
hdfs_endpoint = '/api/hdfs'
const_cluster_status_destroyed = "0"
const_cluster_status_active = "1"
const_cluster_status_pending = "2"
const_cluster_status_failed = "3"
const_hadoop_status_stopped = "0"
const_hadoop_status_started = "1"
const_hadoop_status_format = "2"
const_hadoop_status_pending = const_hadoop_status_format
const_truncate_limit = 350
const_escience_uuid = "ec567bea-4fa2-433d-9935-261a0867ec60"
const_system_uuid = "25ecced9-bf53-4145-91ee-cf47377e9fb2"
HADOOP_STATUS_ACTIONS = {"stop": ["0", "Stopping", "Stopped"],
                         "start": ["1", "Starting", "Started"],
                         "format": ["2", "Formatting", "Formatted"]}

REVERSE_HADOOP_STATUS = {"0":"stop", "1":"start", "2":"Pending"}

# Dictionary of Ansible tags of the hadoop images
hadoop_images_ansible_tags = {"debianbase": {"stop": "stop", "start": "start"},
                              "hadoopbase": {"stop": "stop,FLUMEstop", "start": "start,FLUMEstart"},
                              "hue": {"start": "start,FLUMEstart,HUEstart", "stop": "stop,FLUMEstop,HUEstop"},
                              "ecosystem": {"start": "start,FLUMEstart,ECOSYSTEMstart,HUEstart",
                                            "stop": "stop,FLUMEstop,ECOSYSTEMstop,HUEstop"},
                              "cloudera": {"start": "start,CLOUDstart", "stop": "stop,CLOUDstop"}}
# Dictionary of pithos images UUIDs with their corresponding properties
pithos_images_uuids_properties = {"d3782488-1b6d-479d-8b9b-363494064c52": {"role":"yarn", "tags":"-t preconfig,postconfig", "image":"debianbase"},
                             "3f1f5195-7769-44ba-a4c2-418d86e30f97": {"role":"yarn", "tags":"-t postconfig", "image":"hadoopbase"},
                             "7a8423da-0cfb-414c-9491-1dcb81a87eb6": {"role":"yarn", "tags":"-t postconfig,hueconfig", "image":"hue"},
                             "dc171a3d-09bf-469d-9b7a-d3fb5c0afebc": {"role":"yarn", "tags":"-t postconfig,hueconfig,ecoconfig", "image":"ecosystem"},
                             "05f23bb1-5415-4da3-8e8a-93daa384b2f8": {"role":"cloudera", "tags":"-t preconfig,postconfig", "image":"cloudera"}}
# Dictionary of pithos vre images UUIDs with their corresponding actions
pithos_vre_images_uuids_actions = {"d6593183-39c7-4f64-98fe-e74c49ea00b1": {"image":"drupal","db_name":"db","default_password":"@test123",
                                                                            "update_password":"/usr/bin/mysqladmin -u root -p@test123 password {0}",
                                                                            "change_db_pass":"hash=$(docker exec -t -i drupal bash -c \"php scripts/password-hash.sh {0} | grep hash | sed -e 's#.*hash: \\(\)#\\1#'\")\
                                                                             && echo \\\'$hash|sed -r 's/[$]+/\\\\$/g' 1> hash\
                                                                             && docker exec -t -i db bash -c \"echo \\\"UPDATE users SET pass=`cat hash`\\\">mysql.sql\"\
                                                                             && docker exec -t -i db bash -c \"echo \\\"' where uid='1';\\\">>mysql.sql\"\
                                                                             && docker exec -t -i db bash -c \"mysql -p{0} drupal < mysql.sql\"\
                                                                             && docker exec -t -i db bash -c \"mysql -p{0} -e \\\"use drupal;UPDATE users SET pass=REPLACE(pass, '\n', '');\\\"\"\
                                                                             && rm hash; docker exec -t -i db bash -c \"rm mysql.sql\""},
                               "f64a11dc-97bd-44cb-a502-6c141cc42bfa": {"image":"redmine_redmine_1","db_name":"redmine_postgresql_1","default_password":"password",
                                                                        "update_password":"sudo -u postgres psql -U postgres -d redmine_production -c \"alter user redmine password '{0}';\""
                                                                        ";sed -i \'s/DB_PASS=password/DB_PASS={0}/g\' /usr/local/redmine/docker-compose.yml",
                                                                        "change_db_pass":"docker exec -t -i redmine_redmine_1 bash -c 'RAILS_ENV=production bin/rails runner \"user = User.first ;\
                                                                         user.password, user.password_confirmation = \\\"{0}\\\"; user.save!\"'"},
                               "b1ae3738-b7b3-429e-abef-2fa475f30f0b": {"image":"mediawiki","db_name":"db","default_password":"@test123",
                                                                        "update_password":"/usr/bin/mysqladmin -u root -p@test123 password {0}",
                                                                        "change_db_pass":"docker exec -t -i db bash -c \"mysql -p{0} mediawiki -e \\\"UPDATE user SET user_password = CONCAT(':A:', MD5('{0}')) WHERE user_name = 'Admin';\\\"\""},
                               "6a6676d4-213c-464b-a321-04998c1d8dc7": {"image":"dspace","update_password":"/usr/bin/docker exec -d dspace sudo -u postgres psql -U postgres -d dspace -c \"alter user dspace password '{0}';\"",
                                                                        "change_db_pass":"docker exec -d dspace sed -i 's/db.password *= * *dspace/db.password={0}/g' /dspace/config/dspace.cfg"}}

#encrypt decrypt token in django db
def mask_token(key, token):
    enc = []
    for i in range(len(token)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(token[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def unmask_token(key, masked_token):
    dec = []
    masked_token = base64.urlsafe_b64decode(masked_token.encode('ascii'))
    for i in range(len(masked_token)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(masked_token[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)