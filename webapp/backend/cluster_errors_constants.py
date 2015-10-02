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


error_syntax_clustersize = -1 # Not used anywhere   
error_syntax_cpu_master = -2 # Not used anywhere
error_syntax_ram_master = -3 # Not used anywhere
error_syntax_disk_master = -4 # Not used anywhere
error_syntax_cpu_slave = -5  # Not used anywhere
error_syntax_ram_slave = -6  # Not used anywhere
error_syntax_disk_slave = -7  # Not used anywhere
error_syntax_logging_level = -8  # Not used anywhere
error_syntax_disk_template = -9  # Not used anywhere
error_quotas_cyclades_disk = -10 # Not enough disksize quota in cyclades 
error_quotas_cpu = -11 # Not enough cpu quota in cyclades 
error_quotas_ram = -12 # Not enough ram quota in cyclades
error_quotas_cluster_size = -13 # Not enough VM quota in cyclades
error_quotas_network = -14 # Not enough private network quota 
error_flavor_id = -15 # Not a valid combination of resources
error_image_id = -16 # Not a valid image given
error_syntax_token = -17 # Not used anywhere
error_ready_reroute = -18 # Not used anywhere
error_no_arguments = -19 # Used in orka errors_contants for no arguments given in cli, not used anywhere in backend
error_fatal = -20 # Often used in orka cli for many errors(ClientError,ConnectionError), only once in backend(deletion error in delete vre)
error_user_quota = -22 # Error requesting/getting user quota from ~okeanos
error_flavor_list = -23 # Error requesting/getting flavors list from ~okeanos
error_get_list_servers = -24 # Error requesting/getting user's servers from ~okeanos
error_get_list_projects = -25 # Error requesting/getting user's projects from ~okeanos
error_get_network_quota = -28 # Not used anywhere
error_create_network = -29 # Error creating private network in ~okeanos
error_get_ip = -30 # General floating ip error (e.g. not enough ip quota and error while requesting list of ips)
error_create_server = -31 # Error while creating ~okeanos server (e.g. stay in BUILD status more than 5 minutes).
error_syntax_auth_token = -32 # Error reading ~okeanos token from .kamakirc for cli (e.g. no token in .kamakirc)
error_ansible_playbook = -34 # General error while running create cluster Ansible playbook
error_ssh_client = -35 # Error for staging server not be able to connect to cluster during reroute steps
error_remove_node = -37#Error while removing a node when scaling a cluster
error_cluster_not_exist = -69 # Not used anywhere
error_cluster_corrupt = -70 # Error while deleting cluster and not all VMs are deleted(e.g. Error before deleting all cluster VMs)
error_project_id = -71 # No project id for given project name
error_multiple_entries = -72 # Multiple entries in database for something unique
error_project_quota = -73 # Zero user quota for a given project       
error_authentication = -99 # Invalid token
error_create_dsl = -75#Error while upload dsl file to pithos
error_container = -76#Error pithos container not found while upload dsl file

FNULL = open(os.devnull, 'w') # Redirects whatever is assigned to FNULL to nothingness (e.g. stderr=FNULL)

# Hadoop test command error return status
error_hdfs_test_exit_status = 1 # 1 is error exit status returned from hadoop test commands (e.g. hadoop fs -test -e <some_path> )

# Package constants
ADD_TO_GET_PORT = 9998  # Value offset in order to get slave port numbers, STARTING FROM?...
REPORT = 25             # Define logging level of REPORT
SUMMARY = 29            # Define logging level of SUMMARY
MAX_WAIT = 300          # Max number of seconds for wait function of Cyclades

# MiB <-> GiB easy conversion constants
Mbytes_to_GB = 1024     # Global to convert megabytes to gigabytes
Bytes_to_MB = 1048576   # Global to convert bytes to megabytes
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes

 # Used for storage template conversion in get_flavors_quotas, so user-friendly args can be used in cli and gui
storage_template = {'ext_vlmc':'Archipelago','drbd':'Standard'} # ~okeanos available storage templates with user friendly name
# Reverse storage template not used anywhere
reverse_storage_template = {'Archipelago':'ext_vlmc','Standard':'drbd'} # ~okeanos available storage templates with user friendly name

auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
pithos_url = 'https://pithos.okeanos.grnet.gr/v1'
pithos_put_success = 201  # Success pithos response
pithos_container_not_found = 404

# If no image is given in orka-cli, this is the default image. Not used in backed/cluster_errors_constants
default_image = 'Debian Base'

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

#Set hadoop pending status to 2 (same as hadoop status format and cluster status pending)
const_hadoop_status_pending = const_hadoop_status_format

# If celery message is bigger than following value, it truncates the message. We check if message length is bigger than const_truncate_limit, then add dots (..) at the end of message to indicate truncation. Used for orka cli mainly.
const_truncate_limit = 350
const_escience_uuid = "ec567bea-4fa2-433d-9935-261a0867ec60"
const_system_uuid = "25ecced9-bf53-4145-91ee-cf47377e9fb2"
HADOOP_STATUS_ACTIONS = {"stop": ["0", "Stopping", "Stopped"],
                         "start": ["1", "Starting", "Started"],
                         "format": ["2", "Formatting", "Formatted"],
                         "undefined": ["3", "Undefined", "Undefined"]}

REVERSE_HADOOP_STATUS = {"0":"stop", "1":"start", "2":"Pending", "3":"Undefined"}

# Dictionary of Ansible tags of the hadoop images
hadoop_images_ansible_tags = {"debianbase": {"stop": "stop", "start": "start"},
                              "hadoopbase": {"stop": "stop,FLUMEstop", "start": "start,FLUMEstart"},
                              "hue": {"start": "start,FLUMEstart,HUEstart", "stop": "stop,FLUMEstop,HUEstop"},
                              "ecosystem": {"start": "start,FLUMEstart,ECOSYSTEMstart,HUEstart",
                                            "stop": "stop,FLUMEstop,ECOSYSTEMstop,HUEstop"},
                              "cloudera": {"start": "start,CLOUDstart", "stop": "stop,CLOUDstop"}}

# Dictionary of pithos Hadoop images UUIDs with their corresponding properties
pithos_images_uuids_properties = {"d3782488-1b6d-479d-8b9b-363494064c52": {"role":"yarn", "tags":"-t preconfig,postconfig", "image":"debianbase"},
                             "3f1f5195-7769-44ba-a4c2-418d86e30f97": {"role":"yarn", "tags":"-t postconfig", "image":"hadoopbase"},
                             "7a8423da-0cfb-414c-9491-1dcb81a87eb6": {"role":"yarn", "tags":"-t postconfig,hueconfig", "image":"hue"},
                             "dc171a3d-09bf-469d-9b7a-d3fb5c0afebc": {"role":"yarn", "tags":"-t postconfig,hueconfig,ecoconfig", "image":"ecosystem"},
                             "05f23bb1-5415-4da3-8e8a-93daa384b2f8": {"role":"cloudera", "tags":"-t preconfig,postconfig", "image":"cloudera"}}

# Dictionary of pithos VRE images UUIDs with their corresponding actions
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
                               "c5850bc1-255d-4847-9b89-ce8e86667250": {"image":"dspace","update_password":"/usr/bin/docker exec -d dspace sudo -u postgres psql -U postgres -d dspace -c \"alter user dspace password '{0}';\"",
                                                                        "change_db_pass":"docker exec -d dspace sed -i 's/db.password *= * *dspace/db.password={0}/g' /dspace/config/dspace.cfg"},
                               "0d26fd55-31a4-46b3-955d-d94ecf04a323": {"image":"bigbluebutton"}}

                                                                        
# encrypt/decrypt token in django db
from encrypt_key import key     # File with only one variable key = encrypt_key, keep it outside git
# Encrypts  and decrypts every user's ~okeanos token in database.
encrypt_key = key

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