#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script creates a Hadoop (YARN) cluster on ~okeanos.

@author: e-science Dev-team
"""
import datetime
from time import sleep
import logging
import subprocess
import json
from os.path import join, expanduser
from authenticate_user import unmask_token, encrypt_key
from reroute_ssh import reroute_ssh_prep, start_vre_script
from kamaki.clients import ClientError
from run_ansible_playbooks import install_yarn
from okeanos_utils import Cluster, check_credentials, endpoints_and_user_id, \
    init_cyclades, init_cyclades_netclient, init_plankton, get_project_id, \
    destroy_cluster, get_user_quota, set_cluster_state, retrieve_pending_clusters, get_float_network_id, \
    set_server_state, personality, get_system_dist
from django_db_after_login import db_cluster_create, db_server_create
from cluster_errors_constants import *
from celery import current_task
import os
from rest_framework import status
from backend.models import OrkaImage, VreImage


class YarnCluster(object):
    """
    Class for create hadoop-yarn cluster functionality
    """

    def __init__(self, opts):
        """Initialization of YarnCluster data attributes"""
        self.opts = opts
        # Master VM ip, placeholder value
        self.HOSTNAME_MASTER_IP = '127.0.0.1'
        # master VM root password file, placeholder value
        self.pass_file = 'PLACEHOLDER'
        self.orka_image_uuid = False
        # List of cluster VMs
        self.server_dict = {}
        if self.opts['disk_template'] == 'Archipelago':
            self.opts['disk_template'] = 'ext_vlmc'
        elif self.opts['disk_template'] == 'Standard':
            self.opts['disk_template'] = 'drbd'
        # project id of project name given as argument
        self.project_id = get_project_id(unmask_token(encrypt_key, self.opts['token']),
                                         self.opts['project_name'])
        self.status = {}
        # Instance of an AstakosClient object
        self.auth = check_credentials(unmask_token(encrypt_key, self.opts['token']),
                                      self.opts.get('auth_url',
                                                    auth_url))
        # Check if project has actual quota
        if self.check_project_quota() != 0:
            msg = 'Project %s exists but you have no quota to request' % \
                self.opts['project_name']
            raise ClientError(msg, error_project_quota)
        # ~okeanos endpoints and user id
        self.endpoints, self.user_id = endpoints_and_user_id(self.auth)

        # Instance of CycladesClient
        self.cyclades = init_cyclades(self.endpoints['cyclades'],
                                      unmask_token(encrypt_key, self.opts['token']))
        # Instance of CycladesNetworkClient
        self.net_client = init_cyclades_netclient(self.endpoints['network'],
                                                  unmask_token(encrypt_key, self.opts['token']))
        # Instance of Plankton/ImageClient
        self.plankton = init_plankton(self.endpoints['plankton'],
                                      unmask_token(encrypt_key, self.opts['token']))
        # Get resources of pending clusters
        self.pending_quota = retrieve_pending_clusters(unmask_token(encrypt_key, self.opts['token']),
                                                       self.opts['project_name'])
        self._DispatchCheckers = {}
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_cluster_size_quotas
        # Check for private network availability only when cluster is created
        # and not for Vre server creation
        if self.opts['cluster_size'] > 1:
            self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
                self.check_network_quotas
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_ip_quotas
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_cpu_valid
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_ram_valid
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_disk_valid

    def check_cluster_size_quotas(self):
        """
        Checks if the user quota is enough to create the requested number
        of VMs.
        """
        dict_quotas = get_user_quota(self.auth)
        pending_vm = self.pending_quota['VMs']
        limit_vm = dict_quotas[self.project_id]['cyclades.vm']['limit']
        usage_vm = dict_quotas[self.project_id]['cyclades.vm']['usage']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < self.opts['cluster_size']:
            msg = 'Cyclades VMs out of limit'
            raise ClientError(msg, error_quotas_cluster_size)
        else:
            return 0

    def check_network_quotas(self):
        """
        Checks if the user quota is enough to create a new private network
        Subtracts the number of networks used and pending from the max allowed
        number of networks
        """
        dict_quotas = get_user_quota(self.auth)
        pending_net = self.pending_quota['Network']
        limit_net = dict_quotas[self.project_id]['cyclades.network.private']['limit']
        usage_net = dict_quotas[self.project_id]['cyclades.network.private']['usage']
        project_limit_net = dict_quotas[self.project_id]['cyclades.network.private']['project_limit']
        project_usage_net = dict_quotas[self.project_id]['cyclades.network.private']['project_usage']
        available_networks = limit_net - usage_net
        if (available_networks > (project_limit_net - project_usage_net)):
            available_networks = project_limit_net - project_usage_net
        available_networks -= pending_net
        if available_networks >= 1:
            logging.log(REPORT, ' Private Network quota is ok')
            return 0
        else:
            msg = 'Private Network quota exceeded in project: ' + self.opts['project_name']
            raise ClientError(msg, error_quotas_network)

    def check_ip_quotas(self):
        """Checks user's quota for unattached public ips."""
        dict_quotas = get_user_quota(self.auth)
        list_float_ips = self.net_client.list_floatingips()
        pending_ips = self.pending_quota['Ip']
        limit_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['limit']
        usage_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['usage']

        project_limit_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['project_limit']
        project_usage_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['project_usage']

        available_ips = limit_ips-usage_ips
        if (available_ips > (project_limit_ips - project_usage_ips)): 
            # Quotas are allocated per project and per user account. 
            # So some  other account in the same project may have bind some of user quota since project_quota maybe be different than number_of_users*user_quota
            # The result is user limit quota might be less than it seems so we have to consider project limit as well
            available_ips = project_limit_ips - project_usage_ips
        available_ips -= pending_ips
        for d in list_float_ips:
            if d['instance_id'] is None and d['port_id'] is None:
                available_ips += 1
        if available_ips > 0:
            logging.log(REPORT, ' Floating IP quota is ok')
            return 0
        else:
            msg = 'Floating IP not available in project: ' + self.opts['project_name']
            raise ClientError(msg, error_get_ip)

    def check_cpu_valid(self):
        """
        Checks if the user quota is enough to bind the requested cpu resources.
        Subtracts the number of cpus used and pending from the max allowed
        number of cpus.
        """
        dict_quotas = get_user_quota(self.auth)
        pending_cpu = self.pending_quota['Cpus']
        limit_cpu = dict_quotas[self.project_id]['cyclades.cpu']['limit']
        usage_cpu = dict_quotas[self.project_id]['cyclades.cpu']['usage']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        cpu_req = self.opts['cpu_master'] + \
            self.opts['cpu_slaves'] * (self.opts['cluster_size'] - 1)
        if available_cpu < cpu_req:
            msg = 'Cyclades cpu out of limit'
            raise ClientError(msg, error_quotas_cpu)
        else:
            return 0

    def check_ram_valid(self):
        """
        Checks if the user quota is enough to bind the requested ram resources.
        Subtracts the number of ram used and pending from the max allowed
        number of ram.
        """
        dict_quotas = get_user_quota(self.auth)
        pending_ram = self.pending_quota['Ram']
        limit_ram = dict_quotas[self.project_id]['cyclades.ram']['limit']
        usage_ram = dict_quotas[self.project_id]['cyclades.ram']['usage']
        available_ram = (limit_ram - usage_ram) / Bytes_to_MiB - pending_ram # Convert limit_ram and usage_ram from bytes to MiB to do the subtraction
        ram_req = self.opts['ram_master'] + \
            self.opts['ram_slaves'] * (self.opts['cluster_size'] - 1)
        if available_ram < ram_req:
            msg = 'Cyclades ram out of limit'
            raise ClientError(msg, error_quotas_ram)
        else:
            return 0

    def check_disk_valid(self):
        """
        Checks if the requested disk resources are available for the user.
        Subtracts the number of disk used and pending from the max allowed
        disk size.
        """
        dict_quotas = get_user_quota(self.auth)
        pending_cd = self.pending_quota['Disk']
        limit_cd = dict_quotas[self.project_id]['cyclades.disk']['limit']
        usage_cd = dict_quotas[self.project_id]['cyclades.disk']['usage']
        cyclades_disk_req = self.opts['disk_master'] + \
            self.opts['disk_slaves'] * (self.opts['cluster_size'] - 1)
        available_cyclades_disk_GB = (limit_cd - usage_cd) / Bytes_to_GiB - pending_cd # Convert limit_cd and usage_cd from bytes to GiB to do the subtraction
        if available_cyclades_disk_GB < cyclades_disk_req:
            msg = 'Cyclades disk out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
        else:
            return 0

    def check_all_resources(self):
        """
        Checks user's quota if every requested resource is available.
        Returns zero if everything available.
        """
        for checker in [func for (order, func) in sorted(self._DispatchCheckers.items())]:
            retval = checker()
        return retval

    def get_flavor_id(self, role):
        """
        Return the flavor id for a virtual machine based on cpu, ram, disk_size and
        disk template for selected role (master or slave).
        """
        try:
            flavor_list = self.cyclades.list_flavors(True) # Returns the list of available flavors from cyclades
        except ClientError:
            msg = 'Could not get list of flavors'
            raise ClientError(msg, error_flavor_list)
        flavor_id = 0 # non existing flavor id
        for flavor in flavor_list:
            if flavor['ram'] == self.opts['ram_{0}'.format(role)] and \
                                flavor['SNF:disk_template'] == self.opts['disk_template'] and \
                                flavor['vcpus'] == self.opts['cpu_{0}'.format(role)] and \
                                flavor['disk'] == self.opts['disk_{0}'.format(role)]:
                    flavor_id = flavor['id']

        return flavor_id

    def check_project_quota(self):
        """Checks that for a given project actual quota exist"""
        dict_quotas = get_user_quota(self.auth)
        if self.project_id in dict_quotas:
            return 0
        return error_project_quota
    
    def ssh_key_file(self, name):
        """
        Creates a file named after the timestamped name of cluster
        containing the public ssh_key of the user.
        """
        ssh_info = self.ssh_key_list()
        self.ssh_file = join(os.getcwd(), name.replace(" ", "_") + '_ssh_key')
        for item in ssh_info:
            if item['name'] == self.opts['ssh_key_selection']:
                with open(self.ssh_file, 'w') as f:
                    f.write(item['content'])

    def ssh_key_list(self):
        """
        Get the ssh_key dictionary of a user
        """   
        
        command = 'curl -X GET -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: ' \
                    +  unmask_token(encrypt_key, self.opts['token']) + '" https://cyclades.okeanos.grnet.gr/userdata/keys'
        # get ssh_keys from okeanos server
        p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE , shell = True)
        out, err = p.communicate()
         # out is in string format and it might have more than one entries so we manually convert it to a easier to use
        output = out[2:-2].split('}, {') # [2:-2] removes [{ from the start of the string and }] from the end
                                         # split('}, {') make the string into a list o of dictionaries if multiple entries exists  they are separated with }, { into different elements
        ssh_dict = list()
        ssh_counter = 0
        for dictionary in output:
            mydict = dict()
            new_dictionary = dictionary.replace('"','') # When returned from curl get request each key:value pair is inside  "" which we do not need so we remove those
            dict1 = new_dictionary.split(', ') # create a list in which each element is key: value
            for each in dict1:
                list__keys_values_in_dict = each.split(': ') # separate key from value as elements of a list
                new_list_of_dict_elements = list()
                for item in list__keys_values_in_dict:
                    new_list_of_dict_elements.append(item) # create a list of lists with key value elements
                if len(new_list_of_dict_elements) > 1:
                    for pair in new_list_of_dict_elements:
                        mydict[new_list_of_dict_elements[0]] = new_list_of_dict_elements[1] # create a dictionary with key calue pairs
            ssh_dict.append(mydict)  # creates a list of ssh dictionaries       
        return ssh_dict
        
    def check_user_resources(self):
        """
        Checks user resources before the starting cluster creation.
        Also, returns the flavor id of master and slave VMs and the id of
        the image chosen by the user.
        """
        flavor_master = self.get_flavor_id('master')
        flavor_slaves = self.get_flavor_id('slaves')
        if flavor_master == 0 or flavor_slaves == 0:
            msg = 'Combination of cpu, ram, disk and disk_template do' \
                ' not match an existing id'
            raise ClientError(msg, error_flavor_id)
        retval = self.check_all_resources()
        # check image metadata in database and pithos and set orka_image_uuid accordingly
        self.orka_image_uuid = OrkaImage.objects.get(image_name=self.opts['os_choice']).image_pithos_uuid
        list_current_images = self.plankton.list_public(True, 'default')
        for image in list_current_images:
            if self.orka_image_uuid == image['id']:
                return flavor_master, flavor_slaves, image['id']
        msg = 'Image {0} exists on database but cannot be found or has different id'
        ' on Pithos+'.format(self.opts['os_choice'])
        raise ClientError(msg, error_image_id)         
        
    
    def get_image_id(self):
        """
        Return id of given image
        """
        # check image metadata in database and pithos and set vre_image_uuid accordingly
        chosen_vre_image = VreImage.objects.get(image_name=self.opts['os_choice'])
        self.vre_image_uuid = chosen_vre_image.image_pithos_uuid
        # check if VRE image requires shell script to initialize (e.g BigBlueButton does not require it)
        self.vre_req_script = chosen_vre_image.requires_script
        # Find image id of the operating system arg given
        list_current_images = self.plankton.list_public(True, 'default')
        for image in list_current_images:
            if self.vre_image_uuid == image['id']:
                return image['id']
        msg = 'Image {0} exists on database but cannot be found or has different id'
        ' on Pithos+'.format(self.opts['os_choice'])
        raise ClientError(msg, error_image_id)
       
    def create_vre_server(self):
        """
        Create VRE server in ~okeanos
        """
        vre_script_file_name = ''
        flavor_id = self.get_flavor_id('master')
        if flavor_id == 0:
            msg = 'Combination of cpu, ram, disk and disk_template do' \
                ' not match an existing id'
            raise ClientError(msg, error_flavor_id)
        image_id = self.get_image_id()
        retval = self.check_all_resources()
        pub_keys_path = ''
        vre_script_name = '{0}.sh'.format(filter(lambda l: l.isalpha(), self.opts['os_choice']))
        # Create name of VRE server with [orka] prefix
        vre_server_name = '{0}-{1}'.format('[orka]',self.opts['server_name'])
        self.opts['server_name'] = vre_server_name
        task_id = current_task.request.id
        server_id = db_server_create(self.opts, task_id)
        self.server_name_postfix_id = '{0}-{1}-vre'.format(self.opts['server_name'], server_id)
        # Check if a shell script is required to be copied to VRE server
        if self.vre_req_script:
            vre_script_file_name = 'scripts/{0}'.format(vre_script_name)
        # Check if user chose ssh keys or not.
        ssh_key_selected = self.opts.get('ssh_key_selection','no_ssh_key_selected')
        if ssh_key_selected == 'no_ssh_key_selected' or ssh_key_selected is None:
            self.ssh_file = 'no_ssh_key_selected'
        else:
            self.ssh_key_file(self.server_name_postfix_id)
            pub_keys_path = self.ssh_file
        try:
            server = self.cyclades.create_server(vre_server_name, flavor_id, image_id, personality=personality('', pub_keys_path,vre_script_file_name), project_id=self.project_id)
        except ClientError, e:
            # If no public IP is free, get a new one
            if e.status == status.HTTP_409_CONFLICT:
                get_float_network_id(self.net_client, project_id=self.project_id)
                server = self.cyclades.create_server(vre_server_name, flavor_id, image_id, personality=personality('', pub_keys_path, vre_script_file_name), project_id=self.project_id)
            else:
                msg = u'VRE server \"{0}\" creation failed due to error: {1}'.format(self.opts['server_name'], str(e.args[0]))
                set_server_state(self.opts['token'], server_id, 'Error',status='Failed', error=msg)
                raise
        # Get VRE server root password
        server_pass = server ['adminPass']
        # Placeholder for VRe server public IP
        server_ip = '127.0.0.1'
        # Update DB with server status as pending
        new_state = "Started creation of Virtual Research Environment server {0}".format(vre_server_name)
        subprocess.call('rm ' + self.ssh_file, shell=True)
        set_server_state(self.opts['token'], server_id, new_state, okeanos_server_id=server['id'], password=server_pass)
        new_status = self.cyclades.wait_server(server['id'], max_wait=MAX_WAIT)
        
        if new_status == 'ACTIVE':
            server_details = self.cyclades.get_server_details(server['id'])
            for attachment in server_details['attachments']:
                if attachment['OS-EXT-IPS:type'] == 'floating':
                        server_ip = attachment['ipv4']
        else:
            self.cyclades.delete_server(server['id'])           
            msg = u'VRE server \"{0}\" creation failed because status of VRE server is {1}'.format(self.opts['server_name'],
                                                                                                   new_status)
            set_server_state( self.opts['token'],server_id,'Error',status='Failed',error=msg)
            raise ClientError(msg, error_create_server)
            
        # Wait for VRE server to be pingable
        sleep(30)
        try:
            vre_image_uuid = self.vre_image_uuid
            if vre_image_uuid == server['image']['id']:
                # Check if shell script is required for VRE server
                if self.vre_req_script:
                    start_vre_script(server_ip,server_pass,self.opts['admin_password'], vre_script_name, self.opts['admin_email'])
            else:
                msg = u'VRE server \"{0}\" creation failed. Created okeanos VM id does not match image {1} id'.format(self.opts['server_name'],
                                                                                                                      self.opts['os_choice'])                                                                                   
                set_server_state(self.opts['token'],server_id,'Error',status='Failed',error=msg)
                self.cyclades.delete_server(server['id'])
                raise ClientError(msg, error_image_id) 
        except RuntimeError, e:
            # Exception is raised if a VRE start command is not executed correctly and informs user of its VRE properties
            # so user can ssh connect to the VRE server or delete the server from orkaCLI.
            msg =  u'VRE server \"{0}\" created but started with errors'.format(self.opts['server_name'])
            set_server_state(self.opts['token'],server_id,state='VRE Server created but started with errors',
                             status='Active',server_IP=server_ip, error=msg)
            raise RuntimeError('Your VRE server has the following properties id:{0} root_password:{1} server_IP:{2}'
                               ' but could not be started normally.'.format(server_id,server_pass,server_ip),error_create_server)
        set_server_state(self.opts['token'],server_id,state='VRE Server created',status='Active',server_IP=server_ip)
        return server_id, server_pass, server_ip
        
        
    def create_bare_cluster(self):
        """Creates a bare ~okeanos cluster."""
        server_home_path = expanduser('~')
        server_ssh_keys = join(server_home_path, ".ssh/id_rsa.pub")
        pub_keys_path = ''
        logging.log(SUMMARY, 'Authentication verified')
        current_task.update_state(state="Authenticated")

        flavor_master, flavor_slaves, image_id = self.check_user_resources()
        # Create name of cluster with [orka] prefix
        cluster_name = '%s%s%s' % ('[orka]', '-', self.opts['cluster_name'])
        self.opts['cluster_name'] = cluster_name

        # Update db with cluster status as pending
        task_id = current_task.request.id
        self.cluster_id = db_cluster_create(self.opts, task_id)
        # Append the cluster_id in the cluster name to create a unique name
        # used later for naming various files, e.g. ansible_hosts file and
        # create_cluster_debug file.
        self.cluster_name_postfix_id = '%s%s%s' % (self.opts['cluster_name'], '-', self.cluster_id)

        # Check if user chose ssh keys or not.
        ssh_key_selected = self.opts.get('ssh_key_selection','no_ssh_key_selected')
        if ssh_key_selected == 'no_ssh_key_selected' or ssh_key_selected is None:
            self.ssh_file = 'no_ssh_key_selected'

        else:
            self.ssh_key_file(self.cluster_name_postfix_id)
            pub_keys_path = self.ssh_file

        try:
            cluster = Cluster(self.cyclades, self.opts['cluster_name'],
                              flavor_master, flavor_slaves,
                              image_id, self.opts['cluster_size'],
                              self.net_client, self.auth, self.project_id)

            set_cluster_state(self.opts['token'], self.cluster_id, "Creating ~okeanos cluster (1/3)")

            self.HOSTNAME_MASTER_IP, self.server_dict = \
                cluster.create(server_ssh_keys, pub_keys_path, '')
            sleep(15)
        except Exception, e:
            # If error in bare cluster, update cluster status as destroyed
            set_cluster_state(self.opts['token'], self.cluster_id, 'Error', status='Failed', error=str(e.args[0]))
            subprocess.call('rm ' + self.ssh_file, shell=True)
            raise
        # Get master VM root password
        self.master_root_pass = self.server_dict[0]['adminPass']
        # Return master node ip and server dict
        return self.HOSTNAME_MASTER_IP, self.server_dict

    def create_yarn_cluster(self):
        """Create YARN cluster on a bare ~okeanos cluster """
        try:
            current_task.update_state(state="Started")
            self.HOSTNAME_MASTER_IP, self.server_dict = self.create_bare_cluster()
        except Exception, e:
            logging.error(str(e.args[0]))
            raise
        # Update cluster info with the master VM root password.
        set_cluster_state(self.opts['token'], self.cluster_id,
                          'Configuring YARN cluster node communication (2/3)',
                          password=self.master_root_pass)

        try:
            # Configuring YARN cluster node communication
            list_of_hosts = reroute_ssh_prep(self.server_dict,self.HOSTNAME_MASTER_IP,
                                             linux_dist=get_system_dist(self.opts['os_choice']))
            set_cluster_state(self.opts['token'], self.cluster_id,
                          'Installing and configuring YARN (3/3)')
            # Installing and configuring YARN
            install_yarn(self.opts['token'], list_of_hosts, self.HOSTNAME_MASTER_IP,
                         self.cluster_name_postfix_id, self.orka_image_uuid, self.ssh_file, self.opts['replication_factor'], self.opts['dfs_blocksize'], self.opts['admin_password'])

        except Exception, e:
            logging.error(str(e.args[0]))
            logging.error('Created cluster and resources will be deleted')
            # If error in Yarn cluster, update cluster status as destroyed
            set_cluster_state(self.opts['token'], self.cluster_id, 'Error', status='Failed', error=str(e.args[0]))
            self.destroy('Failed')
            raise

        finally:
            if self.ssh_file != 'no_ssh_key_selected':
                subprocess.call('rm ' + self.ssh_file, shell=True)

        return self.HOSTNAME_MASTER_IP, self.server_dict, self.master_root_pass, self.cluster_id

    def destroy(self, status):
        """Destroy Cluster"""
        return destroy_cluster(self.opts['token'], self.cluster_id, master_IP=self.HOSTNAME_MASTER_IP, status=status)
