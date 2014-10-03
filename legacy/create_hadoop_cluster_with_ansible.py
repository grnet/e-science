#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''

import sys
from sys import argv
from os.path import abspath
from base64 import b64encode
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.pithos import PithosClient
from kamaki.clients.cyclades import CycladesNetworkClient
from kamaki.clients.image import ImageClient
from kamaki.clients.cyclades import CycladesClient
from optparse import OptionParser
from datetime import datetime
import paramiko
from time import sleep
import os
import nose
import logging

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
error_quotas_clustersize = -13
error_quotas_network = -14
error_flavor_id = -15
error_ssh_connection = -16
error_exec_command = -17
error_ready_reroute = -18
error_ssh_copyid_format_start_hadoop = -19
error_fatal = -20
error_cluster_not_exist = -21
error_user_quota = -22
error_flavor_list = -23
error_get_list_servers = -24
error_delete_server = -25
error_delete_network = -26
error_delete_float_ip = -27
error_get_network_quota = -28
error_create_network = -29
error_get_ip = -30
error_create_server = -31
error_syntax_auth_token = -32
error_cluster_corrupt = -33
error_ansible_playbook = -34
error_authentication = -99

# Global constants
MAX_WAIT = 300  # Max number of seconds for wait function of Cyclades
MASTER_SSH_PORT = 22  # Port of master virtual machine for ssh connection
CHAN_TIMEOUT = 360  # Paramiko channel timeout
ADD_TO_GET_PORT = 9998  # Value to add in order to get slave port numbers
CONNECTION_TRIES = 9    # Max number(+1) of connection attempts to a VM
REPORT = 25  # Define logging level of REPORT
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
HREF_VALUE_MINUS_PUBLIC_NETWORK_ID = 56  # IpV4 public network id offset
list_of_hosts = []  # List of dicts wit VM hostnames and their private IPs
PITHOS_FILE = 'elwiki-20140818-pages-meta-current-5000000.xml'  # WordCountFile
FILE_RUN_PI = 'temp_file.txt'  # File used from pi function to write stdout
FILE_KAMAKI = 'kamaki_info.txt'  # File to write kamaki info and retrieve token


def get_ready_for_reroute():
    '''
    Runs pre-setup commands for port forwarding in master virtual machine.
    These commands are executed only.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'apt-get -y install python')
        exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv4/ip_forward')
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth1 -j MASQUERADE')
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth2 -j MASQUERADE')
        exec_command(ssh_client, 'iptables --append FORWARD --in-interface '
                                 'eth2 -j ACCEPT')
    finally:
        ssh_client.close()


def reroute_ssh_to_slaves(dport, slave_ip):
    '''
    For every slave vm in the cluster this function is called.
    Finishes the port forwarding and installs python for ansible
    in every machine. Arguments are the port and the private ip of
    the slave vm.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'iptables -A PREROUTING -t nat -i eth1 -p tcp'
                                 ' --dport '+str(dport)+' -j DNAT --to '
                                 + slave_ip + ':22')
        exec_command(ssh_client, 'iptables -A FORWARD -p tcp -d '
                                 + slave_ip + ' --dport 22 -j ACCEPT')
    finally:
        ssh_client.close()

    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', dport)
    try:
        exec_command(ssh_client, 'route add default gw 192.168.0.2')
        exec_command(ssh_client, 'apt-get -y install python')

    finally:
        ssh_client.close()


class mySSHClient(paramiko.SSHClient):
    '''Class that inherits paramiko SSHClient'''
    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False):
        '''
        Overload paramiko exec_command by adding a timeout.
        Timeout is needed because script hangs when there is not an answer
        from paramiko exec_command,e.g.in a disconnect.
        '''
        chan = self._transport.open_session()
        if get_pty:
            chan.get_pty()
        chan.settimeout(CHAN_TIMEOUT)  # Add a timeout to the exec_command
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)
        return stdin, stdout, stderr


def create_multi_hadoop_cluster(server):
    '''
    Calls every function needed for the installation of hadoop and all
    required dependencies. Also calls the function that formats and starts
    hadoop.
    '''
    dict_s = {}  # Dictionary that will contain fully qualified domain names
    # and private ips temporarily for each machine. It will be appended
    # each time to list_of_hosts. List_of_hosts is the list that has every
    #  fqdn and private ip of the virtual machines.
    for s in server:
        if s['name'].split('-')[-1] == '1':  # Master vm
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': '192.168.0.2',
                      'port': 22}
            global cluster_name
            cluster_name = s['name'].rsplit('-', 1)[0]
            list_of_hosts.append(dict_s)
        else:
            # Every slave ip is increased by 1 from the private ip of the
            # previous slave.The first slave is increased by 1 from the
            # master ip which is 192.168.0.2.
            slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
            port = ADD_TO_GET_PORT+int(s['name'].split('-')[-1])
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': slave_ip,
                      'port': port}
            list_of_hosts.append(dict_s)
    # Pre-setup the port forwarding that will happen later
    try:
        get_ready_for_reroute()
    except Exception, e:
        logging.exception(e.args)
        sys.exit(error_ready_reroute)
    # Port-forwarding now for every slave machine
    for vm in list_of_hosts:
        call_reroute_for_every_vm(vm)
    # Create ansible_hosts file
    try:
        file_name = create_ansible_hosts()
        # Run Ansible playbook
        run_ansible(file_name)
    except Exception, e:
        logging.error(' Program is exiting')
        sys.exit(error_ansible_playbook)
    # create_cluster script finishes the Hadoop configuration
    # after the execution of install-hadoop.yml playbook.
    ssh_client = establish_connect(HOSTNAME_MASTER, 'hduser',
                                   '', MASTER_SSH_PORT)
    # Copy ssh public key from master to every slave
    # Needed for passwordless ssh in hadoop
    try:
        for vm in list_of_hosts:
            if vm['private_ip'] != '192.168.0.2':
                exec_command(ssh_client, 'ssh-copy-id -i ~/.ssh/id_rsa.pub'
                             ' hduser@'+vm['fqdn'].split('.', 1)[0],
                             'ssh_copy_id')
        logging.log(REPORT, " Hadoop is installed and configured")
        # Format and start Hadoop daemons
        format_and_start_hadoop(ssh_client)
    except Exception, e:
        logging.error(e.args)
        sys.exit(error_ssh_copyid_format_start_hadoop)
    finally:
        ssh_client.close()


def run_ansible(filename):
    '''
    Calls the ansible playbook that installs and configures
    hadoop and everything needed for hadoop to be functional.
    Filename as argument is the name of ansible_hosts file.
    '''
    logging.log(REPORT, ' Ansible starts Hadoop installation on master and '
                        'slave nodes')
    # First time call of Ansible playbook install_hadoop.yml executes tasks
    # required for hadoop installation on every virtual machine. Runs with
    # -f flag which is the fork argument of Ansible. Fork number used is size
    # of cluster.
    exit_status = os.system('export ANSIBLE_HOST_KEY_CHECKING=False;'
                            'ansible-playbook -i ' + filename +
                            ' ./ansible_legacy/Hadoop/install.yml -f ' +
                            str(cluster_size))
    if exit_status != 0:
        logging.error(' Ansible failed during Hadoop installation')
        raise RuntimeError

    logging.log(REPORT, ' Ansible executes master-only tasks.')

    # Playbook install_hadoop.yml is called now for tasks executed on master
    # node only. This is why 'the is_master=True' and '-l master' arguments
    # are used.
    exit_status = os.system('ansible-playbook -i ' + filename +
                            ' ./ansible_legacy/Hadoop/install.yml '
                            '-e "is_master=True" -l master')
    if exit_status != 0:
        logging.error(' Ansible failed executing master-only tasks')
        raise RuntimeError

    logging.log(REPORT, ' Ansible executes slave-only tasks.')

    # Playbook install_hadoop.yml is called now for tasks executed on the
    # slave nodes only. That is why 'is_slave=True' and '-l slaves' arguments
    # are used. Also it uses the fork argument for the slave nodes.
    exit_status = os.system('ansible-playbook -i ' + filename +
                            ' ./ansible_legacy/Hadoop/install.yml '
                            '-e "is_slave=True" -l slaves -f '
                            + str(cluster_size-1))
    if exit_status != 0:
        logging.error(' Ansible failed executing slaves-only tasks')
        raise RuntimeError


def format_and_start_hadoop(ssh_client):
    '''
    Runs the commands needed to format the hadoop cluster
    and then start the hadoop daemons.Takes as argument an ssh object
    returned from establish_connect.
    '''
    logging.log(REPORT, ' Formating hadoop')
    exec_command(ssh_client, '/usr/local/hadoop/bin/hadoop'
                             ' namenode -format')
    logging.log(REPORT, ' Starting hadoop')
    exec_command(ssh_client, '/usr/local/hadoop/bin/start-dfs.sh',
                 'ssh_copy_id')
    exec_command(ssh_client, '/usr/local/hadoop/bin/start-mapred.sh')
    logging.log(REPORT, ' Hadoop has started')


def call_reroute_for_every_vm(vm):
    '''Calls reroute_ssh_to_slaves function to finish port forwarding '''
    if vm['port'] != 22:  # Not Master virtual machine
        # Slave virtual machines
        # Forwarding Ports are 10000,10001, etc for every slave vm
        try:
            reroute_ssh_to_slaves(vm['port'], vm['private_ip'])
        except Exception, e:
            logging.exception(e.args)
            os._exit(error_fatal)


def check_command_exit_status(ex_status, command):
    '''
    Checks the exit status of every command executed in virtual machines
    by paramiko exec_command.If the value is different from zero,it raises
    a RuntimeError exception.If the value is zero it logs the appropriate
    message.
    '''
    if ex_status != 0:
            logging.error('Command %s failed to execute with exit status: %d',
                          command, ex_status)
            logging.error('Program shutting down')
            msg = 'Command %s failed with exit status: %d'\
                  % (command, ex_status)
            raise RuntimeError(msg)
    else:
        logging.log(REPORT, ' Command: %s execute with exit status:%d',
                    command, ex_status)


def exec_command(ssh, command, check_command_id=None):
    '''
    Calls overloaded exec_command function of the ssh object given
    as argument. Command is the second argument and its a string.
    check_command_id is used for commands that need additional input after
    exec_command, e.g. ssh-_after_hadoop needs yes[enter].
    '''
    try:
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    except Exception, e:
        logging.exception(e.args)
        raise

    if check_command_id == 'ssh_copy_id':  # For ssh-copy-id
        stdin.flush()
        sleep(5)  # Sleep is necessary for stdin to read yes
        stdin.write('yes\n')
        stdin.flush()
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)

    else:
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)


def establish_connect(hostname, name, passwd, port):
    '''
    Establishes an ssh connection with given hostname, username, password
    and port number.Tries to ping given hostname.If the ping is successfull
    it tries to ssh connect.If an ssh connection is succesful, returns an
    ssh object.If ssh connection fails or throws an exception,logs the error
    and tries to ping again.After a number of failed pings or failed ssh
    connections throws RuntimeError exception.Number of tries is ten.
    '''
    try:
        ssh = mySSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    except:
        logging.error("Failed creating ssh.client")
        raise
    i = 0
    while True:
        response = os.system("ping -c1 -w4 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            try:
                logging.log(REPORT, ' Pinged %s machine,trying to ssh connect'
                            ' at port %s', hostname, port)
                ssh.connect(hostname, username=name, password=passwd,
                            port=port)
                logging.log(REPORT, " Success in ssh connect as %s to %s"
                            " at port %s", name, hostname, str(port))
                return ssh
            except Exception, e:
                logging.warning(e.args)
                logging.warning("Problem in ssh connection as %s to %s at port"
                                " %s trying again", name, hostname, str(port))
                if i > CONNECTION_TRIES:
                    break
                i = i+1
                sleep(1)
        else:
            if i > CONNECTION_TRIES:
                break
            logging.warning('Cannot ping %s machine at port %s, trying again',
                            hostname, str(port))
            i = i+1
            sleep(1)
    ssh.close()
    logging.error("Failed connecting as %s to %s at port %s",
                  name, hostname, str(port))
    logging.error("Program is shutting down")
    msg = 'Failed connecting to %s virtual machine' % hostname
    raise RuntimeError(msg)


def check_credentials(token, auth_url='https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0'):
    '''Identity,Account/Astakos. Test authentication credentials'''
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        logging.error('Authentication failed with url %s and token %s' % (
                      auth_url, token))
        sys.exit(error_authentication)
    logging.log(REPORT, ' Authentication verified')
    return auth


def endpoints_and_user_id(auth):
    '''
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    '''
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
        logging.error('Failed to get endpoints & user_id from identity server')
        raise
    return endpoints, user_id


def init_pithos(endpoint, token, user_id):
    '''
    Object-store / Pithos+.Not used in the script,
    but left for future use
    '''
    logging.log(REPORT, ' Initialize Pithos+ client and'
                'set account to user uuid')
    try:
        return PithosClient(endpoint, token, user_id)
    except ClientError:
        logging.error('Failed to initialize a Pithos+ client')
        raise


def upload_image(pithos, container, image_path):
    '''
    Pithos+/Upload Image
    Not used in the script,but left for future use
    '''
    logging.log(REPORT, ' Create the container "images" and use it')
    try:
        pithos.create_container(container, success=(201, ))
    except ClientError as ce:
        if ce.status in (202, ):
            logging.error('Container %s already exists' % container)
        else:
            logging.error('Failed to create container %s' % container)
            raise
    pithos.container = container

    logging.log(REPORT, ' Upload to "images"')
    with open(abspath(image_path)) as f:
        try:
            pithos.upload_object(
                image_path, f)
        except ClientError:
            logging.error('Failed to upload file %s to container %s' % (
                image_path, container))
            raise


def init_cyclades_netclient(endpoint, token):
    '''
    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating ip
    '''
    logging.log(REPORT, ' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize cyclades network client')
        raise


def init_plankton(endpoint, token):
    '''
    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    '''
    logging.log(REPORT, ' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize the Image client')
        raise


def register_image(plankton, name, user_id, container, path, properties):
    '''
    Image/Plankton.Registers image from Pithos in Plankton.Not used
    but left for future use
    '''
    image_location = (user_id, container, path)
    logging.log(REPORT, ' Register the image')
    try:
        return plankton.register(name, image_location, properties)
    except ClientError:
        logging.error('Failed to register image %s' % name)
        raise


def init_cyclades(endpoint, token):
    '''
    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    '''
    logging.log(REPORT, ' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize cyclades client')
        raise


class Cluster(object):
    '''
    Cluster class represents an entire cluster.Instantiation of cluster gets
    the following arguments: A CycladesClient object,a name-prefix for the
    cluster,the flavors of master and slave machines,the image id of their OS,
    the size of the cluster,a CycladesNetworkClient object and a AstakosClient
    object.
    '''
    def __init__(self, cyclades, prefix, flavor_id_master, flavor_id_slave,
                 image_id, size, net_client, auth_cl):
        self.client = cyclades
        self.nc = net_client
        self.prefix, self.size = prefix, int(size)
        self.flavor_id_master, self.auth = flavor_id_master, auth_cl
        self.flavor_id_slave, self.image_id = flavor_id_slave, image_id

    def get_flo_net_id(self, list_public_networks):
        '''
        Gets an Ipv4 floating network id from the list of public networks Ipv4
        and Ipv6. Takes the href value and removes first 56 characters.
        The number that is left is the public network id
        '''
        float_net_id = 0
        for lst in list_public_networks:
            if(lst['status'] == 'ACTIVE' and
               lst['name'] == 'Public IPv4 Network'):
                    float_net_id = lst['links'][0]['href']
                    break

        try:
            return float_net_id[HREF_VALUE_MINUS_PUBLIC_NETWORK_ID:]
        except TypeError:
            logging.error('Floating Network Id could not be found')
            raise

    def _personality(self, ssh_keys_path='', pub_keys_path=''):
        '''Personality injects ssh keys to the virtual machines we create'''
        personality = []
        if pub_keys_path:
            with open(abspath(pub_keys_path)) as f:
                personality.append(dict(
                    contents=b64encode(f.read()),
                    path='/root/.ssh/authorized_keys',
                    owner='root', group='root', mode=0600))
        if ssh_keys_path or pub_keys_path:
                personality.append(dict(
                    contents=b64encode('StrictHostKeyChecking no'),
                    path='/root/.ssh/config',
                    owner='root', group='root', mode=0600))
        return personality

    def check_network_quota(self):
        '''
        Checks if the user quota is enough to create a new private network
        Subtracts the number of networks used and pending from the max allowed
        number of networks
        '''
        try:
            dict_quotas = self.auth.get_quotas()
        except Exception:
            logging.exception('Error in getting user network quota')
            sys.exit(error_get_network_quota)
        limit_net = dict_quotas['system']['cyclades.network.private']['limit']
        usage_net = dict_quotas['system']['cyclades.network.private']['usage']
        pending_net = \
            dict_quotas['system']['cyclades.network.private']['pending']
        available_networks = limit_net-usage_net-pending_net
        if available_networks >= 1:
            logging.log(REPORT, ' Private Network quota is ok')
            return
        else:
            logging.error('Private Network quota exceeded')
            sys.exit(error_quotas_network)

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        '''
        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        '''
        logging.log(REPORT, ' Create %s servers prefixed as %s',
                    self.size, self.prefix)
        servers = []
        empty_ip_list = []
        list_of_ports = []
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s%s%s' % (date_time, '-', self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = date_time + '-' + self.prefix
        self.check_network_quota()
        # Creates network
        try:
            new_network = self.nc.create_network('MAC_FILTERED', net_name)
        except Exception:
            logging.exception('Error in creating network')
            sys.exit(error_create_network)
        # Gets list of floating ips
        try:
            list_float_ips = self.nc.list_floatingips()
        except Exception:
            logging.exception('Error getting list of floating ips')
            sys.exit(error_get_ip)
        # If there are existing floating ips,we check if there is any free or
        # if all of them are attached to a machine
        if len(list_float_ips) != 0:
            for float_ip in list_float_ips:
                if float_ip['instance_id'] is None:
                    break
                else:
                    count = count+1
                    if count == len(list_float_ips):
                        try:
                            self.nc.create_floatingip(list_float_ips
                                                      [count-1]
                                                      ['floating_network_id'])
                        except ClientError:
                            logging.exception('Cannot create new ip')
                            sys.exit(error_get_ip)
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            try:
                pub_net_list = self.nc.list_networks()
                float_net_id = self.get_flo_net_id(pub_net_list)
                self.nc.create_floatingip(float_net_id)
            except Exception:
                logging.exception('Error in creating float ip')
                sys.exit(error_get_ip)
        logging.log(REPORT, ' Wait for %s servers to build', self.size)

        # Creation of master server

        try:
            servers.append(self.client.create_server(
                server_name, self.flavor_id_master, self.image_id,
                personality=self._personality(ssh_k_path, pub_k_path)))
        except Exception:
            logging.exception('Error creating master virtual machine'
                              % server_name)
            sys.exit(error_create_server)
        # Creation of slave servers
        for i in range(2, self.size+1):
            try:

                server_name = '%s%s%s%s%s' % (date_time,
                                              '-', self.prefix, '-', i)
                servers.append(self.client.create_server(
                    server_name, self.flavor_id_slave, self.image_id,
                    personality=self._personality(ssh_k_path, pub_k_path),
                    networks=empty_ip_list))

            except Exception:
                logging.exception('Error creating server %s' % server_name)
                sys.exit(error_create_server)
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        try:
            new_status = self.client.wait_server(servers[0]['id'],
                                                 max_wait=MAX_WAIT)
            if not new_status:
                logging.error(' Status for server %s is %s',
                              servers[i]['name'], new_status)
                logging.error(' Program shutting down')
                sys.exit(error_create_server)
            logging.log(REPORT, ' Status for server %s is %s',
                        servers[0]['name'], new_status)
            # Create a subnet for the virtual network between master
            #  and slaves along with the ports needed
            self.nc.create_subnet(new_network['id'], '192.168.0.0/24',
                                  enable_dhcp=True)
            port_details = self.nc.create_port(new_network['id'],
                                               servers[0]['id'])
            self.nc.wait_port(port_details['id'], max_wait=MAX_WAIT)
            # Wait server for the slaves, so we can use their server id
            # in port creation
            for i in range(1, self.size):
                new_status = self.client.wait_server(servers[i]['id'],
                                                     max_wait=MAX_WAIT)
                if not new_status:
                    logging.error(' Status for server %s is %s',
                                  servers[i]['name'], new_status)
                    logging.error(' Program shutting down')
                    sys.exit(error_create_server)
                logging.log(REPORT, ' Status for server %s is %s',
                            servers[i]['name'], new_status)
                port_details = self.nc.create_port(new_network['id'],
                                                   servers[i]['id'])
                list_of_ports.append(port_details)

            for port_details in list_of_ports:
                if port_details['status'] == 'BUILD':
                    status = self.nc.wait_port(port_details['id'],
                                               max_wait=MAX_WAIT)
                    if not status:
                        logging.error(' Status for port %s is %s',
                                      port_details['id'], status)
                        logging.error(' Program shutting down')
                        sys.exit(error_create_server)
        except Exception:
            logging.exception('Error in finalizing cluster creation')
            sys.exit(error_create_server)

        if server_log_path:
            logging.info(' Store passwords in file %s', server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)

        # HOSTNAME_MASTER is always the public ip of master node
        global HOSTNAME_MASTER
        try:
            list_of_servers = self.client.list_servers(detail=True)
        except Exception:
            logging.exception('Could not get list of servers.')
            sys.exit(error_get_list_servers)

        # Find our newly created master server in list of servers
        # Then get its public ip and assign it to HOSTNAME_MASTER
        for server in list_of_servers:
            if servers[0]['name'].rsplit('-', 1)[0] == \
                    server['name'].rsplit('-', 1)[0]:
                for attachment in server['attachments']:
                    if attachment['OS-EXT-IPS:type'] == 'floating':
                        HOSTNAME_MASTER = attachment['ipv4']
        return servers


def get_flavor_id(cpu, ram, disk, disk_template, cycladesclient):
    '''Return the flavor id based on cpu,ram,disk_size and disk template'''
    try:
        flavor_list = cycladesclient.list_flavors(True)
    except Exception:
        logging.exception('Could not get list of flavors')
        sys.exit(error_flavor_list)
    flavor_id = 0
    for flavor in flavor_list:
        if flavor['ram'] == ram and \
            flavor['SNF:disk_template'] == disk_template and \
                flavor['vcpus'] == cpu and \
                flavor['disk'] == disk:
            flavor_id = flavor['id']

    return flavor_id


def check_quota(auth, req_quotas):
    '''
    Checks if user quota are enough for what he needed to create the cluster.
    If limit minus (used and pending) are lower or
    higher than what user requests.Also divides with 1024*1024*1024
    to transform bytes to gigabytes.
     '''
    try:
        dict_quotas = auth.get_quotas()
    except Exception:
        logging.exception('Could not get user quota')
        sys.exit(error_user_quota)
    limit_cd = dict_quotas['system']['cyclades.disk']['limit']
    usage_cd = dict_quotas['system']['cyclades.disk']['usage']
    pending_cd = dict_quotas['system']['cyclades.disk']['pending']
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd) / Bytes_to_GB
    if available_cyclades_disk_GB < req_quotas['cyclades_disk']:
        logging.error('Cyclades disk out of limit')
        sys.exit(error_quotas_cyclades_disk)

    limit_cpu = dict_quotas['system']['cyclades.cpu']['limit']
    usage_cpu = dict_quotas['system']['cyclades.cpu']['usage']
    pending_cpu = dict_quotas['system']['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu
    if available_cpu < req_quotas['cpu']:
        logging.error('Cyclades cpu out of limit')
        sys.exit(error_quotas_cpu)

    limit_ram = dict_quotas['system']['cyclades.ram']['limit']
    usage_ram = dict_quotas['system']['cyclades.ram']['usage']
    pending_ram = dict_quotas['system']['cyclades.ram']['pending']
    available_ram = (limit_ram-usage_ram-pending_ram) / Bytes_to_MB
    if available_ram < req_quotas['ram']:
        logging.error('Cyclades ram out of limit')
        sys.exit(error_quotas_ram)
    limit_vm = dict_quotas['system']['cyclades.vm']['limit']
    usage_vm = dict_quotas['system']['cyclades.vm']['usage']
    pending_vm = dict_quotas['system']['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm
    if available_vm < req_quotas['vms']:
        logging.error('Cyclades vms out of limit')
        sys.exit(error_quotas_clustersize)
    logging.log(REPORT, ' Cyclades Cpu,Disk and Ram quotas are ok.')
    return


def create_ansible_hosts():
    '''
    Function that creates the ansible_hosts file and
    returns the name of the file.
    '''
    ansible_hosts_prefix = cluster_name.replace(" ", "")
    ansible_hosts_prefix = ansible_hosts_prefix.replace(":", "")

    # Removes spaces and ':' from cluster name and appends it to ansible_hosts
    # The ansible_hosts file will now have a timestamped name to seperate it
    # from ansible_hosts files of different clusters.
    filename = './ansible_legacy/ansible_hosts' + ansible_hosts_prefix

    # Create ansible_hosts file and write all information that is
    # required from Ansible playbook.
    with open(filename, 'w+') as target:
        target.write('[master]')
        target.write('\n')
        target.write(list_of_hosts[0]['fqdn'])
        target.write(' private_ip='+list_of_hosts[0]['private_ip'])
        target.write(' ansible_ssh_host=' + HOSTNAME_MASTER)
        target.write('\n')
        target.write('\n')
        target.write('[slaves]')
        target.write('\n')

        for host in list_of_hosts[1:]:
            target.write(host['fqdn'])
            target.write(' private_ip='+host['private_ip'])
            target.write(' ansible_ssh_port='+str(host['port']))
            target.write(' ansible_ssh_host='+list_of_hosts[0]['fqdn'])
            target.write("\n")
    return filename


def create_cluster(name, clustersize, cpu_master, ram_master, disk_master,
                   disk_template, cpu_slave, ram_slave, disk_slave, token,
                   image, auth_url='https://accounts.okeanos.grnet.gr'
                   '/identity/v2.0'):
    '''
    This function of our script takes the arguments given and calls the
    check_quota function. Also, calls get_flavor_id to find the matching
    flavor_ids from the arguments given and finds the image id of the
    image given as argument. Then instantiates the Cluster and creates
    the virtual machine cluster of one master and clustersize-1 slaves.
    Calls the function to install hadoop to the cluster.
    '''
    logging.log(REPORT, ' 1.Credentials  and  Endpoints')
    # Finds user public ssh key
    USER_HOME = os.path.expanduser('~')
    global cluster_size
    cluster_size = clustersize
    pub_keys_path = os.path.join(USER_HOME, ".ssh/id_rsa.pub")
    auth = check_credentials(token, auth_url)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    flavor_master = get_flavor_id(cpu_master, ram_master,
                                  disk_master, disk_template,
                                  cyclades)
    flavor_slaves = get_flavor_id(cpu_slave, ram_slave,
                                  disk_slave, disk_template,
                                  cyclades)
    if flavor_master == 0 or flavor_slaves == 0:
        logging.error('Combination of cpu, ram, disk and disk_template do'
                      ' not match an existing id')

        sys.exit(error_flavor_id)
    # Total cpu,ram and disk needed for cluster
    cpu = cpu_master + (cpu_slave)*(clustersize-1)
    ram = ram_master + (ram_slave)*(clustersize-1)
    cyclades_disk = disk_master + (disk_slave)*(clustersize-1)
    # The resources requested by user in a dictionary
    req_quotas = {'cpu': cpu, 'ram': ram, 'cyclades_disk': cyclades_disk,
                  'vms': clustersize}
    check_quota(auth, req_quotas)
    plankton = init_plankton(endpoints['plankton'], token)
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the arg given
    for lst in list_current_images:
        if lst['name'] == image:
            chosen_image = lst

    logging.log(REPORT, ' 2.Create  virtual  cluster')
    cluster = Cluster(cyclades,
                      prefix=name,
                      flavor_id_master=flavor_master,
                      flavor_id_slave=flavor_slaves,
                      image_id=chosen_image['id'],
                      size=clustersize,
                      net_client=init_cyclades_netclient(endpoints['network'],
                                                         token),
                      auth_cl=auth)

    server = cluster.create('', pub_keys_path, '')
    sleep(20)  # Sleep to wait for virtual machines become pingable
    logging.log(REPORT, ' 3.Create Hadoop cluster')
    # Start Hadoop installation
    create_multi_hadoop_cluster(server)
    # Return master node fully qualified domain name
    return HOSTNAME_MASTER


def main(opts):
    '''
    The main function calls create_cluster with the arguments given from
    command line.
    '''
    create_cluster(opts.name, opts.clustersize, opts.cpu_master,
                   opts.ram_master, opts.disk_master, opts.disk_template,
                   opts.cpu_slave, opts.ram_slave, opts.disk_slave,
                   opts.token, opts.image, opts.auth_url)

if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    levels = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'report': REPORT,
              'info': logging.INFO,
              'debug': logging.DEBUG}

    # Create string with all available logging levels
    string_of_levels = ''
    for level_name in levels.keys():
        string_of_levels = string_of_levels + level_name + '|'
    string_of_levels = string_of_levels[:-1]

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="CLUSTER NAME",
                      help='The prefix name of the cluster')
    parser.add_option('--clustersize',
                      action='store', type='int', dest='clustersize',
                      metavar="CLUSTER SIZE",
                      help='Number of virtual cluster nodes to create ')
    parser.add_option('--cpu_master',
                      action='store', type='int', dest='cpu_master',
                      metavar='CPU MASTER',
                      help='Number of cores for the master node')
    parser.add_option('--ram_master',
                      action='store', type='int', dest='ram_master',
                      metavar='RAM MASTER',
                      help='Size of RAM (in MB) for the master node')
    parser.add_option('--disk_master',
                      action='store', type='int', dest='disk_master',
                      metavar='DISK MASTER',
                      help='Disk size (in GB) for the master node')
    parser.add_option('--disk_template',
                      action='store', type='string', dest='disk_template',
                      metavar='DISK TEMPLATE',
                      help='Disk template (drbd, or ext_vlmc)')
    parser.add_option('--cpu_slave',
                      action='store', type='int', dest='cpu_slave',
                      metavar='CPU SLAVE',
                      help='Number of cores for the slave nodes')
    parser.add_option('--ram_slave',
                      action='store', type='int', dest='ram_slave',
                      metavar='RAM SLAVE',
                      help='Size of RAM (in MB) for the slave nodes')
    parser.add_option('--disk_slave',
                      action='store', type='int', dest='disk_slave',
                      metavar='DISK SLAVE',
                      help=' Disk size (in GB) for slave nodes')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')
    parser.add_option('--image',
                      action='store', type='string', dest='image',
                      metavar='IMAGE OS',
                      help='OS for the virtual machine cluster'
                           '.Default=Debian Base',
                      default='Debian Base')

    parser.add_option('--auth_url',
                      action='store', type='string', dest='auth_url',
                      metavar='AUTHENTICATION URL',
                      help='Synnefo authentication url'
                      '.Default=https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0',
                      default='https://accounts.okeanos.grnet.gr'
                              '/identity/v2.0')

    parser.add_option('--logging_level',
                      action='store', type='string', dest='logging_level',
                      metavar='LOGGING LEVEL',
                      help='logging level:[' +
                      string_of_levels +
                      ']. Default is report',
                      default='report')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    #  If clause to catch syntax error in logging argument
    if opts.logging_level not in levels.keys():
        logging.error('invalid syntax for logging_level')
        sys.exit(error_syntax_logging_level)

    logging_level = levels[opts.logging_level]

    if opts.logging_level == 'debug':
        log_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(log_directory, "create_cluster_debug.log")
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging_level, datefmt='%H:%M:%S')

    if opts.clustersize <= 0:
        logging.error('invalid syntax for clustersize'
                      ', clustersize must be a positive integer')
        sys.exit(error_syntax_clustersize)

    if opts.cpu_master <= 0:
        logging.error('invalid syntax for cpu_master'
                      ', cpu_master must be a positive integer')
        sys.exit(error_syntax_cpu_master)

    if opts.ram_master <= 0:
        logging.error('invalid syntax for ram_master'
                      ', ram_master must be a positive integer')
        sys.exit(error_syntax_ram_master)

    if opts.disk_master <= 0:
        logging.error('invalid syntax for disk_master'
                      ', disk_master must be a positive integer')
        sys.exit(error_syntax_disk_master)

    if opts.cpu_slave <= 0:
        logging.error('invalid syntax for cpu_slave'
                      ', cpu_slave must be a positive integer')
        sys.exit(error_syntax_cpu_slave)

    if opts.ram_slave <= 0:
        logging.error('invalid syntax for ram_slave'
                      ', ram_slave must be a positive integer')
        sys.exit(error_syntax_ram_slave)

    if opts.disk_slave <= 0:
        logging.error('invalid syntax for disk_slave'
                      ', disk_slave must be a positive integer')
        sys.exit(error_syntax_disk_slave)

    if opts.disk_template not in ['drbd', 'ext_vlmc']:
        logging.error('invalid syntax for disk_template')
        sys.exit(error_syntax_disk_template)

    if not opts.token:
        logging.error('invalid syntax for authentication token')
        sys.exit(error_syntax_auth_token)

    main(opts)
