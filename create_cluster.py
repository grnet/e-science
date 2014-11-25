#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script creates a cluster on ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
"""
import logging
from argparse import ArgumentParser, ArgumentTypeError
from sys import argv, exit
from time import sleep
from os.path import dirname, abspath, expanduser, join
from reroute_ssh import reroute_ssh_prep
from run_ansible_playbooks import install_yarn
from okeanos_utils import Cluster, check_credentials, endpoints_and_user_id, \
    init_cyclades, init_cyclades_netclient, init_plankton, get_project_id, \
    destroy_cluster
from cluster_errors_constants import *


_defaults = {
    'name': '_Prefix',
    'clustersize': 2,
    'cpu_master': 1,
    'ram_master': 512,
    'disk_master': 5,
    'cpu_slave': 1,
    'ram_slave': 512,
    'disk_slave': 5,
    'disk_template': 'ext_vlmc',
    'image': 'Debian Base',
    'token': 'PLACEHOLDER',
    'auth_url': 'https://accounts.okeanos.grnet.gr/identity/v2.0',
    'yarn': False,
    'logging': 'summary'
}


class _ArgCheck(object):
    """
    Used for type checking arguments supplied for use with type= and
    choices= argparse attributes
    """

    def __init__(self):
        self.logging_levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'summary': SUMMARY,
            'report': REPORT,
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }
        logging.addLevelName(REPORT, "REPORT")
        logging.addLevelName(SUMMARY, "SUMMARY")

    def unsigned_int(self, val):
        """
        :param val: int
        :return: val if val > 0 or raise exception
        """
        ival = int(val)
        if ival < 0:
            raise ArgumentTypeError("%s must be a positive number." % val)
        return ival

    def two_or_bigger(self, val):
        """
        :param val: int
        :return: val if > 2 or raise exception
        """
        ival = int(val)
        if ival < 2:
            raise ArgumentTypeError("%s must be at least 2." % val)
        return ival

    def five_or_bigger(self, val):
        ival = int(val)
        if ival < 5:
            raise ArgumentTypeError("%s must be at least 5." % val)
        return ival


class YarnCluster(object):
    """
    Wrapper class for create hadoop cluster functionality
    """

    def __init__(self, opts):
        if not opts or len(opts) == 0:
            self.opts = _defaults.copy()
        else:
            self.opts = opts
        self.HOSTNAME_MASTER_IP = '127.0.0.1'
        self.server_dict = {}
        self.project_id = get_project_id()
        self.status = {}
        self.auth = check_credentials(self.opts['token'],
                                      self.opts.get('auth_url',
                                                    _defaults['auth_url']))
        self.endpoints, self.user_id = endpoints_and_user_id(self.auth)
        self.cyclades = init_cyclades(self.endpoints['cyclades'],
                                      self.opts['token'])
        self.net_client = init_cyclades_netclient(self.endpoints['network'],
                                                  self.opts['token'])
        self.plankton = init_plankton(self.endpoints['plankton'],
                                      self.opts['token'])
        self._DispatchCheckers = {}
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_clustersize_quotas
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_network_quotas
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_ip_quotas
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_cpu_valid
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_ram_valid
        self._DispatchCheckers[len(self._DispatchCheckers) + 1] = self.check_disk_valid

    def check_clustersize_quotas(self):
        """
        Checks if the user quota is enough to create the requested number
        of vms.
        """
        dict_quotas = self.auth.get_quotas()
        limit_vm = dict_quotas[self.project_id]['cyclades.vm']['limit']
        usage_vm = dict_quotas[self.project_id]['cyclades.vm']['usage']
        pending_vm = dict_quotas[self.project_id]['cyclades.vm']['pending']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < self.opts.get('clustersize', _defaults['clustersize']):
            logging.error('Cyclades vms out of limit')
            return error_quotas_clustersize
        else:
            return 0

    def check_network_quotas(self):
        """
        Checks if the user quota is enough to create a new private network
        Subtracts the number of networks used and pending from the max allowed
        number of networks
        """
        try:
            dict_quotas = self.auth.get_quotas()
        except Exception:
            logging.exception('Error in getting user network quota')
            exit(error_get_network_quota)
        limit_net = dict_quotas[self.project_id]['cyclades.network.private']['limit']
        usage_net = dict_quotas[self.project_id]['cyclades.network.private']['usage']
        pending_net = dict_quotas[self.project_id]['cyclades.network.private']['pending']
        available_networks = limit_net - usage_net - pending_net
        if available_networks >= 1:
            logging.log(REPORT, ' Private Network quota is ok')
            return 0
        else:
            logging.error('Private Network quota exceeded')
            return error_quotas_network

    def check_ip_quotas(self):
        """Checks user's quota for unattached public ips."""
        dict_quotas = self.auth.get_quotas()
        list_float_ips = self.net_client.list_floatingips()
        limit_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['limit']
        usage_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['usage']
        pending_ips = dict_quotas[self.project_id]['cyclades.floating_ip']['pending']
        available_ips = limit_ips - (usage_ips + pending_ips)
        for d in list_float_ips:
            if d['instance_id'] is None and d['port_id'] is None:
                available_ips += 1
        if available_ips > 0:
            return 0
        else:
            logging.error('Floating IP not available')
            return error_get_ip

    def check_cpu_valid(self):
        """
        Checks if the user quota is enough to bind the requested cpu resources.
        Subtracts the number of cpus used and pending from the max allowed
        number of cpus.
        """
        dict_quotas = self.auth.get_quotas()
        limit_cpu = dict_quotas[self.project_id]['cyclades.cpu']['limit']
        usage_cpu = dict_quotas[self.project_id]['cyclades.cpu']['usage']
        pending_cpu = dict_quotas[self.project_id]['cyclades.cpu']['pending']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        cpu_req = self.opts.get('cpu_master', _defaults['cpu_master']) + \
                  (self.opts.get('cpu_slave', _defaults['cpu_slave']) * (
                      self.opts.get('clustersize', _defaults['clustersize']) - 1))
        if available_cpu < cpu_req:
            logging.error('Cyclades cpu out of limit')
            return error_quotas_cpu
        else:
            return 0

    def check_ram_valid(self):
        """
        Checks if the user quota is enough to bind the requested ram resources.
        Subtracts the number of ram used and pending from the max allowed
        number of ram.
        """
        dict_quotas = self.auth.get_quotas()
        limit_ram = dict_quotas[self.project_id]['cyclades.ram']['limit']
        usage_ram = dict_quotas[self.project_id]['cyclades.ram']['usage']
        pending_ram = dict_quotas[self.project_id]['cyclades.ram']['pending']
        available_ram = (limit_ram - usage_ram - pending_ram) / Bytes_to_MB
        ram_req = self.opts.get('ram_master', _defaults['ram_master']) + \
                    (self.opts.get('ram_slave', _defaults['ram_slave']) * (
                    self.opts.get('clustersize', _defaults['clustersize']) - 1))
        if available_ram < ram_req:
            logging.error('Cyclades ram out of limit')
            return error_quotas_ram
        else:
            return 0

    def check_disk_valid(self):
        """
        Checks if the user quota is enough to bind the requested disk resources.
        Subtracts the number of disk used and pending from the max allowed
        disk size.
        """
        dict_quotas = self.auth.get_quotas()
        limit_cd = dict_quotas[self.project_id]['cyclades.disk']['limit']
        usage_cd = dict_quotas[self.project_id]['cyclades.disk']['usage']
        pending_cd = dict_quotas[self.project_id]['cyclades.disk']['pending']
        cyclades_disk_req = self.opts.get('disk_master', _defaults['disk_master']) + \
                            (self.opts.get('disk_slave', _defaults['disk_slave']) *
                             (self.opts.get('clustersize', _defaults['clustersize']) - 1))
        available_cyclades_disk_GB = (limit_cd - usage_cd - pending_cd) / Bytes_to_GB
        if available_cyclades_disk_GB < cyclades_disk_req:
            logging.error('Cyclades disk out of limit')
            return error_quotas_cyclades_disk
        else:
            return 0

    def check_all_resources(self):
        """
        Checks user's quota if every requested resource is available.
        """
        for checker in [func for (order, func) in sorted(self._DispatchCheckers.items())]:
            # for k, checker in self._DispatchCheckers.iteritems():
            retval = checker()
            if retval != 0:
                logging.error(checker.__name__ + " failed")
                return retval
        logging.log(REPORT, "All checks passed.")
        return 0

    def get_flavor_id_master(self, cyclades_client):
        """
        Return the flavor id for the master based on cpu,ram,disk_size and
        disk template
        """
        try:
            flavor_list = cyclades_client.list_flavors(True)
        except Exception:
            logging.exception('Could not get list of flavors')
            exit(error_flavor_list)
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
        except Exception:
            logging.exception('Could not get list of flavors')
            exit(error_flavor_list)
        flavor_id = 0
        for flavor in flavor_list:
            if flavor['ram'] == self.opts['ram_slave'] and \
                            flavor['SNF:disk_template'] == self.opts['disk_template'] and \
                            flavor['vcpus'] == self.opts['cpu_slave'] and \
                            flavor['disk'] == self.opts['disk_slave']:
                flavor_id = flavor['id']

        return flavor_id

    def create_bare_cluster(self):
        """
        This method of our class takes the arguments given and calls the
         function. Also, calls get_flavor_id to find the matching
        flavor_ids from the arguments given and finds the image id of the
        image given as argument. Then instantiates the Cluster and creates
        the virtual machine cluster of one master and clustersize-1 slaves.
        """
        # Finds user public ssh key
        USER_HOME = expanduser('~')
        chosen_image = {}
        pub_keys_path = join(USER_HOME, ".ssh/id_rsa.pub")
        logging.log(SUMMARY, ' Authentication verified')
        flavor_master = self.get_flavor_id_master(self.cyclades)
        flavor_slaves = self.get_flavor_id_slave(self.cyclades)
        if flavor_master == 0 or flavor_slaves == 0:
            logging.error('Combination of cpu, ram, disk and disk_template do'
                          ' not match an existing id')

            exit(error_flavor_id)
        list_current_images = self.plankton.list_public(True, 'default')
        # Check availability of resources
        retval = self.check_all_resources()
        if retval != 0:
            exit(retval)
        # Find image id of the operating system arg given
        for lst in list_current_images:
            if lst['name'] == self.opts['image']:
                chosen_image = lst
                break
        if not chosen_image:
            logging.error(self.opts['image']+' is not a valid image')
            exit(error_image_id)
        logging.log(SUMMARY, ' Creating ~okeanos cluster')
        cluster = Cluster(self.cyclades,
                          prefix=self.opts['name'],
                          flavor_id_master=flavor_master,
                          flavor_id_slave=flavor_slaves,
                          image_id=chosen_image['id'],
                          size=self.opts['clustersize'],
                          net_client=self.net_client,
                          auth_cl=self.auth)

        self.HOSTNAME_MASTER_IP, self.server_dict = cluster.create('', pub_keys_path, '')
        sleep(15)
        # wait for the machines to be pingable
        logging.log(SUMMARY, ' ~okeanos cluster created')
        # Return master node ip and server dict
        return self.HOSTNAME_MASTER_IP, self.server_dict

    def destroy(self):
        """Destroy cluster object"""
        destroy_cluster(self.server_dict, self.opts['token'])

    def create_yarn_cluster(self):
        """Create e-Science Yarn cluster"""
        self.HOSTNAME_MASTER_IP, self.server_dict = self.create_bare_cluster()
        logging.log(SUMMARY, ' Creating e-Science Yarn cluster')
        list_of_hosts = reroute_ssh_prep(self.server_dict, self.HOSTNAME_MASTER_IP)
        logging.log(SUMMARY, ' Installing and configuring Yarn')
        install_yarn(list_of_hosts, self.HOSTNAME_MASTER_IP, self.opts['name'])
        return self.HOSTNAME_MASTER_IP, self.server_dict


def main(opts):
    """
    The main function calls create_cluster or resource check methods with
    the arguments given from command line.
    """
    c_yarn_cluster = YarnCluster(opts)
    if opts['yarn']:
        c_yarn_cluster.create_yarn_cluster()
    else:
        c_yarn_cluster.create_bare_cluster()


if __name__ == "__main__":
    parser = ArgumentParser()
    checker = _ArgCheck()
    parser.add_argument("--name", help='The prefix name of the cluster',
                        dest='name', default='Test')

    parser.add_argument("--clustersize", help='Number of virtual cluster nodes to create',
                        dest='clustersize', type=checker.two_or_bigger,
                        default=_defaults['clustersize'])

    parser.add_argument("--cpu_master", help='Number of cpu cores for the master node',
                        dest='cpu_master', type=int,
                        default=_defaults['cpu_master'])

    parser.add_argument("--ram_master", help='Size of RAM (MB) for the master node',
                        dest='ram_master', type=checker.unsigned_int,
                        default=_defaults['ram_master'])

    parser.add_argument("--disk_master", help='Disk size (GB) for the master node',
                        dest='disk_master', type=checker.five_or_bigger,
                        default=_defaults['disk_master'])

    parser.add_argument("--cpu_slave", help='Number of cpu cores for the slave node(s)',
                        dest='cpu_slave', type=int,
                        default=_defaults['cpu_slave'])

    parser.add_argument("--ram_slave", help='Size of RAM (MB) for the slave node(s)',
                        dest='ram_slave', type=int,
                        default=_defaults['ram_slave'])

    parser.add_argument("--disk_slave", help='Disk size (GB) for the slave node(s)',
                        dest='disk_slave', type=checker.five_or_bigger,
                        default=_defaults['disk_slave'])

    parser.add_argument("--disk_template", help='Disk template',
                        dest='disk_template',
                        default=_defaults['disk_template'],
                        choices=['drbd', 'ext_vlmc'])

    parser.add_argument("--image", help='OS for the virtual machine cluster',
                        dest='image', default=_defaults['image'])

    parser.add_argument("--token", help='Synnefo authentication token',
                        dest='token', default=_defaults['token'])

    parser.add_argument("--auth_url", nargs='?', dest='auth_url',
                        default=_defaults['auth_url'],
                        help='Synnefo authentication url')

    parser.add_argument("--yarn", "-y", dest='yarn', action='store_true',
                        help='Create a Yarn type cluster')

    parser.add_argument("--logging", nargs='?', dest='logging',
                        default=_defaults['logging'],
                        choices=checker.logging_levels,
                        help='Logging Level. Default: summary')

    if len(argv) > 1:
        opts = vars(parser.parse_args(argv[1:]))
        if opts['logging'] == 'debug':
            log_directory = dirname(abspath(__file__))
            log_file_path = join(log_directory, "create_cluster_debug.log")
            logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                                level=checker.logging_levels[opts['logging']], datefmt='%H:%M:%S')
        main(opts)
    else:
        parser.parse_args('-h'.split())
        exit()
