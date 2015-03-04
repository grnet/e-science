#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains useful classes and fuctions for orka package.

@author: Ioannis Stenos, Nick Vrionis
"""
import logging
from base64 import b64encode
from os.path import abspath
from kamaki.clients import ClientError
from kamaki.clients.image import ImageClient
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.compute import ComputeClient
from kamaki.clients.cyclades import CycladesClient, CycladesNetworkClient
from time import sleep
from cluster_errors_constants import *
from celery import current_task
from django_db_after_login import db_cluster_update, get_user_id
from backend.models import UserInfo, ClusterInfo
# Global constants
MAX_WAIT = 300  # Max number of seconds for wait function of Cyclades



def retrieve_pending_clusters(token, project_name):
    """Retrieve pending cluster info"""
    uuid = get_user_id(token)
    pending_quota = {"VMs": 0, "Cpus": 0, "Ram": 0, "Disk": 0, "Ip": 0,
                     "Network": 0}
    user = UserInfo.objects.get(uuid=uuid)
    # Get clusters with pending status
    pending_clusters = ClusterInfo.objects.filter(user_id=user,
                                                  project_name=project_name,
                                                  cluster_status="2")
    if pending_clusters:
        # Get all pending resources
        # excluding ip and network (always zero pending as a convention
        # for the time being)
        vm_sum, vm_cpu, vm_ram, vm_disk = 0, 0, 0, 0
        for cluster in pending_clusters:
            vm_sum = vm_sum + cluster.cluster_size
            vm_cpu = vm_cpu + cluster.cpu_master + cluster.cpu_slaves*(cluster.cluster_size - 1)
            vm_ram = vm_ram + cluster.mem_master + cluster.mem_slaves*(cluster.cluster_size - 1)
            vm_disk = vm_disk + cluster.disk_master + cluster.disk_slaves*(cluster.cluster_size - 1)

        pending_quota = {"VMs": vm_sum, "Cpus": vm_cpu, "Ram": vm_ram,
                         "Disk": vm_disk, "Ip": 0,
                         "Network": 0}

    return pending_quota

def set_cluster_state(token, cluster_id, state, status='Pending', master_IP='', password=''):
    """
    Logs a cluster state message and updates the celery and escience database
    state.
    """
    logging.log(SUMMARY, state)
    db_cluster_update(token, status, cluster_id, master_IP, state=state, password=password)
    if len(state) > 349:
        state = state[:348] + '..'
    current_task.update_state(state=state)


def get_project_id(token, project_name):
    """
    Return the id of an active ~okeanos project.
    """
    auth = check_credentials(token)
    dict_quotas = auth.get_quotas()
    try:
        list_of_projects = auth.get_projects(state='active')
    except ClientError:
        msg = ' Could not get list of active projects'
        raise ClientError(msg, error_get_list_projects)
    for project in list_of_projects:
        if project['name'] == project_name and project['id'] in dict_quotas:
            return project['id']
    msg = ' No project id was found for ' + project_name
    raise ClientError(msg, error_proj_id)


def destroy_cluster(token, cluster_id, master_IP=''):
    """
    Destroys cluster and deletes network and floating ip. Finds the machines
    that belong to the cluster from the cluster id that is given. Cluster id
    is the unique integer that each cluster has in escience database.
    """
    current_task.update_state(state=" Started")
    servers_to_delete = []
    cluster_to_delete = ClusterInfo.objects.get(id=cluster_id)
    if cluster_to_delete.master_IP:
        float_ip_to_delete = cluster_to_delete.master_IP
    else:
        float_ip_to_delete = master_IP
    list_of_errors = []
    master_id = None
    network_to_delete_id = None
    float_ip_to_delete_id = None
    new_status = 'placeholder'
    auth = check_credentials(token)
    current_task.update_state(state=" Authenticated")
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    nc = init_cyclades_netclient(endpoints['network'], token)
    # Get list of servers and public ips
    try:
        list_of_servers = cyclades.list_servers(detail=True)
        list_of_ips = nc.list_floatingips()
    except ClientError:
        msg = 'Could not get list of resources.'\
            'Cannot delete cluster'
        raise ClientError(msg, error_get_list_servers)

    # Get master virtual machine and network from ip
    for ip in list_of_ips:
        if ip['floating_ip_address'] == float_ip_to_delete:
            master_id = ip['instance_id']
            float_ip_to_delete_id = ip['id']
            master_server = cyclades.get_server_details(master_id)
            for attachment in master_server['attachments']:
                if (attachment['OS-EXT-IPS:type'] == 'fixed' and
                        not attachment['ipv6']):
                    network_to_delete_id = attachment['network_id']
                    break
            break
    # Show an error message and exit if not valid ip or network
    if not master_id:
        msg = ' [%s] is not the valid public ip of the master' % \
            float_ip_to_delete
        raise ClientError(msg, error_get_ip)

    if not network_to_delete_id:
        cyclades.delete_server(master_id)
        set_cluster_state(token, cluster_id, " Deleted master VM", status='Destroyed')
        msg = ' A valid network of master and slaves was not found.'\
            'Deleting the master VM only'
        raise ClientError(msg, error_cluster_corrupt)

    # Get the servers of the cluster to be deleted
    for server in list_of_servers:
        for attachment in server['attachments']:
            if attachment['network_id'] == network_to_delete_id:
                servers_to_delete.append(server)
                break
    cluster_name = servers_to_delete[0]['name'].rsplit("-", 1)[0]
    number_of_nodes = len(servers_to_delete)
    set_cluster_state(token, cluster_id, " Starting deletion of requested cluster")
    # Start cluster deleting
    try:
        for server in servers_to_delete:
            cyclades.delete_server(server['id'])
        state= ' Deleting %d servers ' % number_of_nodes
        set_cluster_state(token, cluster_id, state)
        # Wait for every server of the cluster to be deleted
        for server in servers_to_delete:
            new_status = cyclades.wait_server(server['id'],
                                              current_status='ACTIVE',
                                              max_wait=MAX_WAIT)
            if new_status != 'DELETED':
                logging.error(' Error deleting server [%s]' % server['name'])
                list_of_errors.append(error_cluster_corrupt)
        set_cluster_state(token, cluster_id, ' Deleting cluster network and public ip')
    except ClientError:
        logging.exception(' Error in deleting server')
        list_of_errors.append(error_cluster_corrupt)

    try:
        nc.delete_network(network_to_delete_id)
        state= ' Network with id [%s] is deleted' % network_to_delete_id
        set_cluster_state(token, cluster_id, state)
        sleep(10)  # Take some time to ensure it is deleted
    except ClientError:
        logging.exception(' Error in deleting network')
        list_of_errors.append(error_cluster_corrupt)

    # Delete the floating ip of deleted cluster
    try:
        nc.delete_floatingip(float_ip_to_delete_id)
        state= ' Floating ip [%s] is deleted' % float_ip_to_delete
        logging.log(SUMMARY, state)
        set_cluster_state(token, cluster_id, state)
    except ClientError:
        logging.exception(' Error in deleting floating ip [%s]' %
                          float_ip_to_delete)
        list_of_errors.append(error_cluster_corrupt)

    state= ' Cluster with public IP [%s] was deleted ' % float_ip_to_delete
    set_cluster_state(token, cluster_id, state, status='Destroyed')
    # Everything deleted as expected
    if not list_of_errors:
        return cluster_name
    # There was one or more errors, return error message
    else:
        msg = ' Error while deleting cluster'
        raise ClientError(msg, list_of_errors[0])


def check_credentials(token, auth_url=auth_url):
    """Identity,Account/Astakos. Test authentication credentials"""
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        msg = ' Authentication failed with url %s and token %s'\
            % (auth_url, token)
        raise ClientError(msg, error_authentication)
    return auth


def get_flavor_id(token):
    """From kamaki flavor list get all possible flavors """
    auth = check_credentials(token)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    try:
        flavor_list = cyclades.list_flavors(True)
    except ClientError:
        msg = ' Could not get list of flavors'
        raise ClientError(msg, error_flavor_list)
    cpu_list = []
    ram_list = []
    disk_list = []
    disk_template_list = []

    for flavor in flavor_list:
        if flavor['vcpus'] not in cpu_list:
            cpu_list.append(flavor['vcpus'])
        if flavor['ram'] not in ram_list:
            ram_list.append(flavor['ram'])
        if flavor['disk'] not in disk_list:
            disk_list.append(flavor['disk'])
        if flavor['SNF:disk_template'] not in disk_template_list:
            disk_template_list.append(flavor['SNF:disk_template'])
    cpu_list = sorted(cpu_list)
    ram_list = sorted(ram_list)
    disk_list = sorted(disk_list)
    flavors = {'cpus': cpu_list, 'ram': ram_list,
               'disk': disk_list, 'disk_template': disk_template_list}
    return flavors


def get_user_quota(auth):
    """Return user quota"""
    try:
        return auth.get_quotas()
    except ClientError:
        msg = ' Could not get user quota'
        raise ClientError(msg, error_user_quota)


def check_quota(token, project_id):
    """
    Checks if user available quota .
    Available = limit minus (~ okeanos used and escience pending).
    Also divides with 1024*1024*1024 to transform bytes to gigabytes.
    """
    auth = check_credentials(token)
    dict_quotas = get_user_quota(auth)
    project_name = auth.get_project(project_id)['name']
    # Get pending quota for given project id
    pending_quota = retrieve_pending_clusters(token, project_name)

    limit_cd = dict_quotas[project_id]['cyclades.disk']['limit'] / Bytes_to_GB
    usage_cd = dict_quotas[project_id]['cyclades.disk']['usage'] / Bytes_to_GB
    project_limit_cd = dict_quotas[project_id]['cyclades.disk']['project_limit'] / Bytes_to_GB
    project_usage_cd = dict_quotas[project_id]['cyclades.disk']['project_usage'] / Bytes_to_GB
    pending_cd = pending_quota['Disk']
    available_cyclades_disk_GB = limit_cd-usage_cd
    if (available_cyclades_disk_GB > (project_limit_cd - project_usage_cd)):
        available_cyclades_disk_GB = project_limit_cd - project_usage_cd
    available_cyclades_disk_GB = available_cyclades_disk_GB - pending_cd

    limit_cpu = dict_quotas[project_id]['cyclades.cpu']['limit']
    usage_cpu = dict_quotas[project_id]['cyclades.cpu']['usage']
    project_limit_cpu = dict_quotas[project_id]['cyclades.cpu']['project_limit']
    project_usage_cpu = dict_quotas[project_id]['cyclades.cpu']['project_usage']
    pending_cpu = pending_quota['Cpus']
    available_cpu = limit_cpu - usage_cpu
    if (available_cpu > (project_limit_cpu - project_usage_cpu)):
        available_cpu = project_limit_cpu - project_usage_cpu
    available_cpu = available_cpu - pending_cpu

    limit_ram = dict_quotas[project_id]['cyclades.ram']['limit'] / Bytes_to_MB
    usage_ram = dict_quotas[project_id]['cyclades.ram']['usage'] / Bytes_to_MB
    project_limit_ram = dict_quotas[project_id]['cyclades.ram']['project_limit'] / Bytes_to_MB
    project_usage_ram = dict_quotas[project_id]['cyclades.ram']['project_usage'] / Bytes_to_MB
    pending_ram = pending_quota['Ram']
    available_ram = limit_ram-usage_ram
    if (available_ram > (project_limit_ram - project_usage_ram)):
        available_ram = project_limit_ram - project_usage_ram
    available_ram = available_ram - pending_ram

    limit_vm = dict_quotas[project_id]['cyclades.vm']['limit']
    usage_vm = dict_quotas[project_id]['cyclades.vm']['usage']
    project_limit_vm = dict_quotas[project_id]['cyclades.vm']['project_limit']
    project_usage_vm = dict_quotas[project_id]['cyclades.vm']['project_usage']
    pending_vm = pending_quota['VMs']
    available_vm = limit_vm-usage_vm
    if (available_vm > (project_limit_vm - project_usage_vm)):
        available_vm = project_limit_vm - project_usage_vm
    available_vm = available_vm - pending_vm


    quotas = {'cpus': {'limit': limit_cpu, 'available': available_cpu},
              'ram': {'limit': limit_ram, 'available': available_ram},
              'disk': {'limit': limit_cd,
                       'available': available_cyclades_disk_GB},
              'cluster_size': {'limit': limit_vm, 'available': available_vm}}
    return quotas


def check_images(token, project_id):
    """
    Checks the list of the current images
    Filter the ones that match with our uuid
    Return the available images
    """
    auth = check_credentials(token)
    endpoints, user_id = endpoints_and_user_id(auth)    
    plankton = init_plankton(endpoints['plankton'], token)
    list_current_images = plankton.list_public(True, 'default')
    available_images = []
    for image in list_current_images:
        # owner of image will be checked based on the uuid
        if image['owner'] == "ec567bea-4fa2-433d-9935-261a0867ec60":
            available_images.append(image['name'])
        elif image['owner'] == "25ecced9-bf53-4145-91ee-cf47377e9fb2" and image['name'] == "Debian Base":
            available_images.append(image['name'])
                
    return available_images

def endpoints_and_user_id(auth):
    """
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    """
    logging.log(REPORT, ' Get the endpoints')
    try:
        endpoints = dict(
            astakos=auth.get_service_endpoints('identity')['publicURL'],
            cyclades=auth.get_service_endpoints('compute')['publicURL'],
            pithos=auth.get_service_endpoints('object-store')['publicURL'],
            plankton=auth.get_service_endpoints('image')['publicURL'],
            network=auth.get_service_endpoints('network')['publicURL']
            )
        user_id = auth.user_info['id']
    except ClientError:
        msg = ' Failed to get endpoints & user_id from identity server'
        raise ClientError(msg)
    return endpoints, user_id


def init_cyclades_netclient(endpoint, token):
    """
    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating ip
    """
    logging.log(REPORT, ' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades network client'
        raise ClientError(msg)


def init_plankton(endpoint, token):
    """
    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    """
    logging.log(REPORT, ' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize the Image client'
        raise ClientError(msg)


def init_cyclades(endpoint, token):
    """
    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    """
    logging.log(REPORT, ' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades client'
        raise ClientError(msg)


class Cluster(object):
    """
    Cluster class represents an entire ~okeanos cluster.Instantiation of
    cluster gets the following arguments: A CycladesClient object,a name-prefix
    for the cluster,the flavors of master and slave machines,the image id of
    their OS, the size of the cluster,a CycladesNetworkClient object, an
    AstakosClient object and the project_id.
    """
    def __init__(self, cyclades, prefix, flavor_id_master, flavor_id_slave,
                 image_id, size, net_client, auth_cl, project_id):
        self.client = cyclades
        self.nc = net_client
        self.prefix, self.size = prefix, int(size)
        self.flavor_id_master, self.auth = flavor_id_master, auth_cl
        self.flavor_id_slave, self.image_id = flavor_id_slave, image_id
        self.project_id = project_id

    def get_flo_net_id(self):
        """
        Gets an Ipv4 floating network id from the list of public networks Ipv4
        """
        pub_net_list = self.nc.list_networks()
        float_net_id = 1
        i = 1
        for lst in pub_net_list:
            if(lst['status'] == 'ACTIVE' and
               lst['name'] == 'Public IPv4 Network'):
                float_net_id = lst['id']
                try:
                    self.nc.create_floatingip(float_net_id, project_id=self.project_id)
                    return 0
                except ClientError:
                    if i < len(pub_net_list):
                        i = i+1

        return error_get_ip

    def _personality(self, ssh_keys_path='', pub_keys_path=''):
        """Personality injects ssh keys to the virtual machines we create"""
        personality = []
        if ssh_keys_path and pub_keys_path:
            try:
                with open(abspath(ssh_keys_path)) as f1, open(abspath(pub_keys_path)) as f2:
                    personality.append(dict(
                        contents=b64encode(f1.read() + f2.read()),
                        path='/root/.ssh/authorized_keys',
                        owner='root', group='root', mode=0600))
            except IOError:
                msg = " No valid public ssh key(id_rsa.pub) in %s or %s" %((abspath(ssh_keys_path)),(abspath(pub_keys_path)))
                raise IOError(msg)
        elif ssh_keys_path:
            try:
                with open(abspath(ssh_keys_path)) as f:
                    personality.append(dict(
                        contents=b64encode(f.read()),
                        path='/root/.ssh/authorized_keys',
                        owner='root', group='root', mode=0600))
            except IOError:
                msg = " No valid public ssh key(id_rsa.pub) in " + (abspath(ssh_keys_path))
                raise IOError(msg)
        if ssh_keys_path or pub_keys_path:
                personality.append(dict(
                    contents=b64encode('StrictHostKeyChecking no'),
                    path='/root/.ssh/config',
                    owner='root', group='root', mode=0600))
        return personality

    def clean_up(self, servers=None, network=None):
        """Delete resources after a failed attempt to create a cluster"""
        if not (network and servers):
            logging.error(' Nothing to delete')
            return
        logging.error(' An unrecoverable error occured in ~okeanos.'
                      'Cleaning up and shutting down')
        status = ''
        if servers:
            for server in servers:
                status = self.client.get_server_details(server['id'])['status']

                if status == 'BUILD':
                    status = self.client.wait_server(server['id'],
                                                     max_wait=MAX_WAIT)
                self.client.delete_server(server['id'])

                new_status = self.client.wait_server(server['id'],
                                                     current_status=status,
                                                     max_wait=MAX_WAIT)
                logging.log(REPORT, ' Server [%s] is being %s', server['name'],
                            new_status)
                if new_status != 'DELETED':
                    logging.error(' Error deleting server [%s]' % server['name'])
        if network:
            self.nc.delete_network(network['id'])

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        """
        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        """
        logging.log(REPORT, ' Create %s servers prefixed as [%s]',
                    self.size, self.prefix)
        servers = []
        empty_ip_list = []
        list_of_ports = []
        count = 0
        hostname_master = ''
        i = 0
        port_status = ''
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s' % (self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = self.prefix
        # Creates network
        try:
            new_network = self.nc.create_network('MAC_FILTERED', net_name,
                                                 project_id=self.project_id)
        except ClientError:
            msg = ' Error in creating network'
            raise ClientError(msg, error_create_network)

        # Gets list of floating ips
        try:
            list_float_ips = self.nc.list_floatingips()
        except ClientError:
            self.clean_up(network=new_network)
            msg = ' Error getting list of floating ips'
            raise ClientError(msg, error_get_ip)
        # If there are existing floating ips,we check if there is any free or
        # if all of them are attached to a machine
        if len(list_float_ips) != 0:
            for float_ip in list_float_ips:
                if float_ip['instance_id'] is None and float_ip['port_id'] is None:
                    break
                else:
                    count = count+1
                    if count == len(list_float_ips):
                        try:
                            self.nc.create_floatingip(list_float_ips
                                                      [count-1]
                                                      ['floating_network_id'],
                                                      project_id=self.project_id)
                        except ClientError:
                            if self.get_flo_net_id() != 0:
                                self.clean_up(network=new_network)
                                msg = ' Error in creating float ip'
                                raise ClientError(msg, error_get_ip)
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            if self.get_flo_net_id() != 0:
                self.clean_up(network=new_network)
                msg = ' Error in creating float ip'
                raise ClientError(msg, error_get_ip)
        logging.log(REPORT, ' Wait for %s servers to build', self.size)

        # Creation of master server

        try:
            servers.append(self.client.create_server(
                server_name, self.flavor_id_master, self.image_id,
                personality=self._personality(ssh_k_path, pub_k_path),
                project_id=self.project_id))
        except ClientError:
            self.clean_up(servers=servers, network=new_network)
            msg = ' Error creating master VM [%s]' % server_name
            raise ClientError(msg, error_create_server)
        # Creation of slave servers
        for i in range(2, self.size+1):
            try:

                server_name = '%s%s%s' % (self.prefix, '-', i)
                servers.append(self.client.create_server(
                    server_name, self.flavor_id_slave, self.image_id,
                    personality=self._personality(ssh_k_path, pub_k_path),
                    networks=empty_ip_list, project_id=self.project_id))

            except ClientError:
                self.clean_up(servers=servers, network=new_network)
                msg = ' Error creating server [%s]' % server_name
                raise ClientError(msg, error_create_server)
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        try:
            new_status = self.client.wait_server(servers[0]['id'],
                                                 max_wait=MAX_WAIT)
            if new_status != 'ACTIVE':
                msg = ' Status for server [%s] is %s' % \
                    (servers[i]['name'], new_status)
                raise ClientError(msg, error_create_server)
            logging.log(REPORT, ' Status for server [%s] is %s',
                        servers[0]['name'], new_status)
            # Create a subnet for the virtual network between master
            #  and slaves along with the ports needed
            self.nc.create_subnet(new_network['id'], '192.168.0.0/24',
                                  enable_dhcp=True)
            port_details = self.nc.create_port(new_network['id'],
                                               servers[0]['id'])
            port_status = self.nc.wait_port(port_details['id'],
                                            max_wait=MAX_WAIT)
            if port_status != 'ACTIVE':
                msg = ' Status for port [%s] is %s' % \
                    (port_details['id'], port_status)
                raise ClientError(msg, error_create_server)
            # Wait server for the slaves, so we can use their server id
            # in port creation
            for i in range(1, self.size):
                new_status = self.client.wait_server(servers[i]['id'],
                                                     max_wait=MAX_WAIT)
                if new_status != 'ACTIVE':
                    msg = ' Status for server [%s] is %s' % \
                        (servers[i]['name'], new_status)
                    raise ClientError(msg, error_create_server)
                logging.log(REPORT, ' Status for server [%s] is %s',
                            servers[i]['name'], new_status)
                port_details = self.nc.create_port(new_network['id'],
                                                   servers[i]['id'])
                list_of_ports.append(port_details)

            for port in list_of_ports:
                port_status = self.nc.get_port_details(port['id'])['status']
                if port_status == 'BUILD':
                    port_status = self.nc.wait_port(port['id'],
                                                    max_wait=MAX_WAIT)
                if port_status != 'ACTIVE':
                    msg = ' Status for port [%s] is %s' % \
                        (port['id'], port_status)
                    raise ClientError(msg, error_create_server)
        except Exception:
            self.clean_up(servers=servers, network=new_network)
            raise

        if server_log_path:
            logging.info(' Store passwords in file [%s]', server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)

        # hostname_master is always the public ip of master node
        master_details = self.client.get_server_details(servers[0]['id'])
        for attachment in master_details['attachments']:
            if attachment['OS-EXT-IPS:type'] == 'floating':
                        hostname_master = attachment['ipv4']
        return hostname_master, servers
