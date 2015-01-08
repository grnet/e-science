#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script creates a cluster on ~okeanos.

@author: Ioannis Stenos, Nick Vrionis, George Tzelepis
"""
import datetime
from time import sleep
import logging
from os.path import join, expanduser
from reroute_ssh import reroute_ssh_prep
from kamaki.clients import ClientError
from run_ansible_playbooks import install_yarn
from okeanos_utils import Cluster, check_credentials, endpoints_and_user_id, \
    init_cyclades, init_cyclades_netclient, init_plankton, get_project_id, \
    destroy_cluster, get_user_quota, authenticate_escience, OrkaRequest
from cluster_errors_constants import *


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
        # project id of project name given as argument
        self.project_id = get_project_id(self.opts['token'],
                                         self.opts['project_name'])
        self.status = {}
        self.escience_token = authenticate_escience(self.opts['token'])
        self.orka_request = OrkaRequest(self.escience_token,
                                   {"orka":{"project_name":self.opts['project_name']}})
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
        if 'use_hadoop_image' in self.opts:
            if self.opts['use_hadoop_image']:
                self.hadoop_image = True

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
        pending_quota = self.orka_request.retrieve_quota()
        pending_vm = pending_quota['orka']['VMs']
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
        pending_quota = self.orka_request.retrieve_quota()
        pending_net = pending_quota['orka']['Network']
        limit_net = dict_quotas[self.project_id]['cyclades.network.private']['limit']
        usage_net = dict_quotas[self.project_id]['cyclades.network.private']['usage']
        available_networks = limit_net - usage_net - pending_net
        if available_networks >= 1:
            logging.log(REPORT, ' Private Network quota is ok')
            return 0
        else:
            msg = 'Private Network quota exceeded'
            raise ClientError(msg, error_quotas_network)

    def check_ip_quotas(self):
        """Checks user's quota for unattached public ips."""
        dict_quotas = get_user_quota(self.auth)
        list_float_ips = self.net_client.list_floatingips()
        pending_quota = self.orka_request.retrieve_quota()
        pending_ips = pending_quota['orka']['Ip']
        limit_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['limit']
        usage_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['usage']
        available_ips = limit_ips - usage_ips - pending_ips
        for d in list_float_ips:
            if d['instance_id'] is None and d['port_id'] is None:
                available_ips += 1
        if available_ips > 0:
            return 0
        else:
            msg = 'Floating IP not available'
            raise ClientError(msg, error_get_ip)

    def check_cpu_valid(self):
        """
        Checks if the user quota is enough to bind the requested cpu resources.
        Subtracts the number of cpus used and pending from the max allowed
        number of cpus.
        """
        dict_quotas = get_user_quota(self.auth)
        pending_quota = self.orka_request.retrieve_quota()
        pending_cpu = pending_quota['orka']['Cpus']
        limit_cpu = dict_quotas[self.project_id]['cyclades.cpu']['limit']
        usage_cpu = dict_quotas[self.project_id]['cyclades.cpu']['usage']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        cpu_req = self.opts['cpu_master'] + \
            self.opts['cpu_slave'] * (self.opts['cluster_size'] - 1)
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
        pending_quota = self.orka_request.retrieve_quota()
        pending_ram = pending_quota['orka']['Ram']
        limit_ram = dict_quotas[self.project_id]['cyclades.ram']['limit']
        usage_ram = dict_quotas[self.project_id]['cyclades.ram']['usage']
        available_ram = (limit_ram - usage_ram) / Bytes_to_MB - pending_ram
        ram_req = self.opts['ram_master'] + \
            self.opts['ram_slave'] * (self.opts['cluster_size'] - 1)
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
        pending_quota = self.orka_request.retrieve_quota()
        pending_cd = pending_quota['orka']['Disk']
        limit_cd = dict_quotas[self.project_id]['cyclades.disk']['limit']
        usage_cd = dict_quotas[self.project_id]['cyclades.disk']['usage']
        cyclades_disk_req = self.opts['disk_master'] + \
            self.opts['disk_slave'] * (self.opts['cluster_size'] - 1)
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
        return 0

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
            if flavor['ram'] == self.opts['ram_slave'] and \
                            flavor['SNF:disk_template'] == self.opts['disk_template'] and \
                            flavor['vcpus'] == self.opts['cpu_slave'] and \
                            flavor['disk'] == self.opts['disk_slave']:
                flavor_id = flavor['id']

        return flavor_id

    def create_password_file(self, master_root_pass, master_name):
        """
        Creates a file named after the timestamped name of master node
        containing the root password of the master virtual machine of
        the cluster.
        """
        self.pass_file = join('./', master_name + '_root_password')
        self.pass_file = self.pass_file.replace(" ", "")
        with open(self.pass_file, 'w') as f:
            f.write(master_root_pass)

    def check_project_quota(self):
        """Checks that for a given project actual quota exist"""
        dict_quotas = get_user_quota(self.auth)
        if self.project_id in dict_quotas:
            return 0
        return error_project_quota

    def create_bare_cluster(self):
        """Creates a bare ~okeanos cluster."""
        # Finds user public ssh key
        USER_HOME = expanduser('~')
        chosen_image = {}
        pub_keys_path = join(USER_HOME, ".ssh/id_rsa.pub")
        logging.log(SUMMARY, ' Authentication verified')
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
            if lst['name'] == self.opts['image']:
                chosen_image = lst
                break
        if not chosen_image:
            msg = self.opts['image']+' is not a valid image'
            raise ClientError(msg, error_image_id)
        logging.log(SUMMARY, ' Creating ~okeanos cluster')

        # Create timestamped name of the cluster
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cluster_name = '%s%s%s' % (date_time, '-', self.opts['name'])
        self.opts['name'] = cluster_name

        # Update db with cluster status as pending

        payload = {"orka": {"cluster_name": self.opts['name'],
                            "cluster_size": self.opts['cluster_size'],
                            "cpu_master": self.opts['cpu_master'],
                            "mem_master": self.opts['ram_master'],
                            "disk_master": self.opts['disk_master'],
                            "cpu_slaves": self.opts['cpu_slave'],
                            "mem_slaves": self.opts['ram_slave'],
                            "disk_slaves": self.opts['disk_slave'],
                            "disk_template": self.opts['disk_template'],
                            "os_choice": self.opts['image'],
                            "project_name": self.opts['project_name']}}

        orka_req = OrkaRequest(self.escience_token, payload)
        orka_req.create_cluster_db()
        try:
            cluster = Cluster(self.cyclades, self.opts['name'],
                              flavor_master, flavor_slaves,
                              chosen_image['id'], self.opts['cluster_size'],
                              self.net_client, self.auth, self.project_id)

            self.HOSTNAME_MASTER_IP, self.server_dict = \
                cluster.create('', pub_keys_path, '')
            sleep(15)
        except Exception:
            # If error in bare cluster, update cluster status as destroyed
            payload = {"orka": {"status": "Destroyed", "cluster_name": self.opts['name'], "master_ip": "placeholder"}}
            orka_req_error = OrkaRequest(self.escience_token, payload)
            orka_req_error.update_cluster_db()
            raise
        # wait for the machines to be pingable
        logging.log(SUMMARY, ' ~okeanos cluster created')
        # Get master VM root password
        master_root_pass = self.server_dict[0]['adminPass']
        master_name = self.server_dict[0]['name']
        # Write master VM root password to a file with same name as master VM
        self.create_password_file(master_root_pass, master_name)
        # Return master node ip and server dict
        return self.HOSTNAME_MASTER_IP, self.server_dict

    def create_yarn_cluster(self):
        """Create Yarn cluster"""
        try:
            self.HOSTNAME_MASTER_IP, self.server_dict = self.create_bare_cluster()
        except Exception, e:
            logging.error(' Fatal error: ' + str(e.args[0]))
            raise
        logging.log(SUMMARY, ' Creating Yarn cluster')
        try:
            list_of_hosts = reroute_ssh_prep(self.server_dict,
                                             self.HOSTNAME_MASTER_IP)

            logging.log(SUMMARY, ' Installing and configuring Yarn')
            install_yarn(list_of_hosts, self.HOSTNAME_MASTER_IP,
                         self.server_dict[0]['name'], self.hadoop_image)
            logging.log(SUMMARY, ' The root password of master VM [%s] '
                        'is on file %s', self.server_dict[0]['name'],
                        self.pass_file)
            # If Yarn cluster is build, update cluster status as active
            payload = {"orka": {"status": "Active", "cluster_name":self.opts['name'], "master_ip": self.HOSTNAME_MASTER_IP}}
            orka_req = OrkaRequest(self.escience_token, payload)
            orka_req.update_cluster_db()
            return self.HOSTNAME_MASTER_IP, self.server_dict
        except Exception, e:
            logging.error(' Fatal error:' + str(e.args[0]))
            logging.error(' Created cluster and resources will be deleted')
            # If error in Yarn cluster, update cluster status as destroyed
            payload = {"orka": {"status": "Destroyed", "cluster_name": self.opts['name'], "master_ip": "placeholder"}}
            orka_req_error = OrkaRequest(self.escience_token, payload)
            orka_req_error.update_cluster_db()
            self.destroy()
            raise

    def destroy(self):
        """Destroy Cluster"""
        destroy_cluster(self.opts['token'], self.HOSTNAME_MASTER_IP)
