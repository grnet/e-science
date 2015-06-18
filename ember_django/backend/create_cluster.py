#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script creates a HadoopYarn cluster on ~okeanos.

@author: Ioannis Stenos, Nick Vrionis, George Tzelepis
"""
import datetime
from time import sleep
import logging
import subprocess
import json
from os.path import join, expanduser
from reroute_ssh import reroute_ssh_prep
from kamaki.clients import ClientError
from run_ansible_playbooks import install_yarn
from okeanos_utils import Cluster, check_credentials, endpoints_and_user_id, \
    init_cyclades, init_cyclades_netclient, init_plankton, get_project_id, \
    destroy_cluster, get_user_quota, set_cluster_state, retrieve_pending_clusters
from django_db_after_login import db_cluster_create
from cluster_errors_constants import *
from celery import current_task
import os


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
        self.hadoop_image = False
        # List of cluster VMs
        self.server_dict = {}
        if self.opts['disk_template'] == 'Archipelago':
            self.opts['disk_template'] = 'ext_vlmc'
        elif self.opts['disk_template'] == 'Standard':
            self.opts['disk_template'] = 'drbd'
        # project id of project name given as argument
        self.project_id = get_project_id(self.opts['token'],
                                         self.opts['project_name'])
        self.status = {}
        # Instance of an AstakosClient object
        self.auth = check_credentials(self.opts['token'],
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
                                      self.opts['token'])
        # Instance of CycladesNetworkClient
        self.net_client = init_cyclades_netclient(self.endpoints['network'],
                                                  self.opts['token'])
        # Instance of Plankton/ImageClient
        self.plankton = init_plankton(self.endpoints['plankton'],
                                      self.opts['token'])
        # Get resources of pending clusters
        self.pending_quota = retrieve_pending_clusters(self.opts['token'],
                                                       self.opts['project_name'])
        # check escienceconf flag and set hadoop_image accordingly
        list_current_images = self.plankton.list_public(True, 'default')
        for image in list_current_images:
            if self.opts['os_choice'] == image['name']:
                if 'escienceconf' in image['properties']:
                    image_metadata = json.loads(image['properties']['escienceconf'])
                    if image_metadata['ecosystem'] == 'True':
                        self.hadoop_image = 'ecosystem'
                    elif image_metadata['cloudera'] == 'True':
                        self.hadoop_image = 'cloudera'
                    elif image_metadata['hadoop'] == 'True' and image_metadata['hue'] == 'True':
                        self.hadoop_image = 'hue'
                    else:
                        self.hadoop_image = 'hadoopbase'
                else:
                    self.hadoop_image = 'debianbase'

        self._DispatchCheckers = {}
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] =\
            self.check_cluster_size_quotas
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
        available_ram = (limit_ram - usage_ram) / Bytes_to_MB - pending_ram
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
        available_cyclades_disk_GB = (limit_cd - usage_cd) / Bytes_to_GB - pending_cd
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
            # for k, checker in self._DispatchCheckers.iteritems():
            retval = checker()
            # print checker.__name__ + ":" + str(retval) #debug
        return retval

    def get_flavor_id_master(self, cyclades_client):
        """
        Return the flavor id for the master based on cpu,ram,disk_size and
        disk template
        """
        try:
            flavor_list = cyclades_client.list_flavors(True)
        except ClientError:
            msg = 'Could not get list of flavors'
            raise ClientError(msg, error_flavor_list)
        flavor_id = 0
        for flavor in flavor_list:
            if flavor['ram'] == self.opts['ram_master'] and \
                                flavor['SNF:disk_template'] == self.opts['disk_template'] and \
                                flavor['vcpus'] == self.opts['cpu_master'] and \
                                flavor['disk'] == self.opts['disk_master']:
                    flavor_id = flavor['id']

        return flavor_id

    def get_flavor_id_slave(self, cyclades_client):
        """
        Return the flavor id for the slave based on cpu,ram,disk_size and
        disk template
        """
        try:
            flavor_list = cyclades_client.list_flavors(True)
        except ClientError:
            msg = 'Could not get list of flavors'
            raise ClientError(msg, error_flavor_list)
        flavor_id = 0
        for flavor in flavor_list:
            if flavor['ram'] == self.opts['ram_slaves'] and \
                                flavor['SNF:disk_template'] == self.opts['disk_template'] and \
                                flavor['vcpus'] == self.opts['cpu_slaves'] and \
                                flavor['disk'] == self.opts['disk_slaves']:
                    flavor_id = flavor['id']

        return flavor_id


    def check_project_quota(self):
        """Checks that for a given project actual quota exist"""
        dict_quotas = get_user_quota(self.auth)
        if self.project_id in dict_quotas:
            return 0
        return error_project_quota
    
    def ssh_key_file(self, cluster_name):
        """
        Creates a file named after the timestamped name of cluster
        containing the public ssh_key of the user.
        """
        ssh_info = self.ssh_key_list()
        cluster_name = cluster_name.replace(" ", "_")
        self.ssh_file = join(os.getcwd(), cluster_name + '_ssh_key')
        for item in ssh_info:
            if item['name'] == self.opts['ssh_key_selection']:
                with open(self.ssh_file, 'w') as f:
                    f.write(item['content'])

    def ssh_key_list(self):
        """
        Get the ssh_key dictionary of a user
        """   
        command = 'curl -X GET -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: ' + self.opts['token'] + '" https://cyclades.okeanos.grnet.gr/userdata/keys'
        p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE , shell = True)
        out, err = p.communicate()
        output = out[2:-2].split('}, {')
        ssh_dict = list()
        ssh_counter = 0
        for dictionary in output:
            mydict = dict()
            new_dictionary = dictionary.replace('"','')
            dict1 = new_dictionary.split(', ')
            for each in dict1:
                list__keys_values_in_dict = each.split(': ')
                new_list_of_dict_elements = list()
                for item in list__keys_values_in_dict:
                    new_list_of_dict_elements.append(item)
                if len(new_list_of_dict_elements) > 1:
                    for pair in new_list_of_dict_elements:
                        mydict[new_list_of_dict_elements[0]] = new_list_of_dict_elements[1]
            ssh_dict.append(mydict)          
        return ssh_dict
        
    def check_user_resources(self):
        """
        Checks user resources before the starting cluster creation.
        Also, returns the flavor id of master and slave VMS and the id of
        the image chosen by the user.
        """
        chosen_image = {}
        flavor_master = self.get_flavor_id_master(self.cyclades)
        flavor_slaves = self.get_flavor_id_slave(self.cyclades)
        if flavor_master == 0 or flavor_slaves == 0:
            msg = 'Combination of cpu, ram, disk and disk_template do' \
                ' not match an existing id'
            raise ClientError(msg, error_flavor_id)

        list_current_images = self.plankton.list_public(True, 'default')
        # Check availability of resources
        retval = self.check_all_resources()
        # Find image id of the operating system arg given
        for lst in list_current_images:
            if lst['name'] == self.opts['os_choice']:
                chosen_image = lst
                break
        if not chosen_image:
            msg = self.opts['os_choice']+' is not a valid image'
            raise ClientError(msg, error_image_id)

        return flavor_master, flavor_slaves, chosen_image['id']

    def create_bare_cluster(self):
        """Creates a bare ~okeanos cluster."""
        server_home_path = expanduser('~')
        server_ssh_keys = join(server_home_path, ".ssh/id_rsa.pub")
        pub_keys_path = ''
        logging.log(SUMMARY, ' Authentication verified')
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
        if self.opts['ssh_key_selection'] is None or self.opts['ssh_key_selection'] == 'no_ssh_key_selected':
            self.ssh_file = 'no_ssh_key_selected'

        else:
            self.ssh_key_file(self.cluster_name_postfix_id)
            pub_keys_path = self.ssh_file

        try:
            cluster = Cluster(self.cyclades, self.opts['cluster_name'],
                              flavor_master, flavor_slaves,
                              image_id, self.opts['cluster_size'],
                              self.net_client, self.auth, self.project_id)

            set_cluster_state(self.opts['token'], self.cluster_id, " Creating ~okeanos cluster (1/3)")

            self.HOSTNAME_MASTER_IP, self.server_dict = \
                cluster.create(server_ssh_keys, pub_keys_path, '')
            sleep(15)
        except Exception:
            # If error in bare cluster, update cluster status as destroyed
            set_cluster_state(self.opts['token'], self.cluster_id, 'Error', status='Destroyed')
            os.system('rm ' + self.ssh_file)
            raise
        # Get master VM root password
        self.master_root_pass = self.server_dict[0]['adminPass']
        # Return master node ip and server dict
        return self.HOSTNAME_MASTER_IP, self.server_dict

    def create_yarn_cluster(self):
        """Create Yarn cluster"""
        try:
            current_task.update_state(state=" Started")
            self.HOSTNAME_MASTER_IP, self.server_dict = self.create_bare_cluster()
        except Exception, e:
            logging.error(' Fatal error: ' + str(e.args[0]))
            raise
        # Update cluster info with the master VM root password.
        set_cluster_state(self.opts['token'], self.cluster_id,
                          ' Configuring YARN cluster node communication (2/3)',
                          password=self.master_root_pass)

        try:
            list_of_hosts = reroute_ssh_prep(self.server_dict,
                                             self.HOSTNAME_MASTER_IP)
            set_cluster_state(self.opts['token'], self.cluster_id,
                          ' Installing and configuring YARN (3/3)')

            install_yarn(self.opts['token'], list_of_hosts, self.HOSTNAME_MASTER_IP,
                         self.cluster_name_postfix_id, self.hadoop_image, self.ssh_file, self.opts['replication_factor'], self.opts['dfs_blocksize'])

        except Exception, e:
            logging.error(' Fatal error:' + str(e.args[0]))
            logging.error(' Created cluster and resources will be deleted')
            # If error in Yarn cluster, update cluster status as destroyed
            set_cluster_state(self.opts['token'], self.cluster_id, 'Error')
            #self.destroy()
            raise

        finally:
            if self.ssh_file != 'no_ssh_key_selected':
                os.system('rm ' + self.ssh_file)

        return self.HOSTNAME_MASTER_IP, self.server_dict, self.master_root_pass, self.cluster_id

    def destroy(self):
        """Destroy Cluster"""
        destroy_cluster(self.opts['token'], self.cluster_id, master_IP=self.HOSTNAME_MASTER_IP)
