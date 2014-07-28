'''
Created on 22 Jul 2014

@author: developer
'''
import sys
from sys import argv
from os.path import abspath
from base64 import b64encode
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from datetime import datetime
import paramiko
sys.stderr = open('/dev/null')
sys.stderr = sys.__stderr__
import time
from time import sleep
import os
import nose
import threading
import logging
error_syntax_clustersize = -1
error_syntax_cpu_master = -2
error_syntax_ram_master = -3
error_syntax_disk_master = -4
error_syntax_cpu_slave = -5
error_syntax_ram_slave = -6
error_syntax_disk_slave = -7
error_syntax_disk_template= -8
error_quotas_cyclades_disk = -9
error_quotas_cpu = -10
error_quotas_ram = -11
error_quotas_clustersize = -12
error_quotas_netwrok = -13
error_flavor_id = -14
error_ssh_connection = -15
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
threadLock = threading.Lock()

'''
REMEMBER TO DISABLE SELINUX.
Not sure if needed.
Could be for hadoop running.
'''


def configuration_bashrc(ssh_client):
    '''
    Configures .bashrc for hduser.Adds hadoop_home, java_home
    and useful aliases. Also adds java_home to hadoop-env.sh
    '''
    logging.info('Start configuring bashrc')
    exec_command(ssh_client, 'echo "export HADOOP_HOME=/usr/local/hadoop"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "export JAVA_HOME=/usr/lib/jvm/java-7-'
                             'oracle" >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "unalias fs &> /dev/null"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo \'alias fs="hadoop fs"\' >> .bashrc', 0)
    exec_command(ssh_client, 'echo "unalias hls &> /dev/null"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo \'alias hls="fs -ls"\' >> .bashrc', 0)
    exec_command(ssh_client, 'source ~/.bashrc', 0)
    exec_command(ssh_client, 'echo "export PATH=$PATH:$HADOOP_HOME/bin"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "export JAVA_HOME=/usr/lib/jvm/java-7-'
                             'oracle" >>'
                             ' /usr/local/hadoop/conf/hadoop-env.sh', 0)
    logging.error('Done configuring bashrc')
    

def get_ready_for_reroute():
    '''
    Runs setup commands for port forwarding in master virtual machine.
    These commands are executed only once before the threads start.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', 22)
    exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv4/ip_forward', 0)
    exec_command(ssh_client, 'iptables --table nat --append POSTROUTING --out-'
                             'interface eth1 -j MASQUERADE', 0)
    exec_command(ssh_client, 'iptables --table nat --append POSTROUTING --out-'
                             'interface eth2 -j MASQUERADE', 0)
    exec_command(ssh_client, 'iptables --append FORWARD --in-interface eth2'
                             ' -j ACCEPT', 0)
    ssh_client.close()


def reroute_ssh_to_slaves(dport, slave_ip):
    '''
    Every thread-slave virtual machine connects to master and setups
    its port forwarding rules with the port and private ip of the slave.
    Also connects to itself and adds the master as a default gateway,
    so the slave has internet access through master vm.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', 22)
    exec_command(ssh_client, 'iptables -A PREROUTING -t nat -i eth1 -p tcp'
                             ' --dport '+str(dport)+' -j DNAT --to ' + slave_ip
                             + ':22', 0)
    exec_command(ssh_client, 'iptables -A FORWARD -p tcp -d '+slave_ip +
                             ' --dport 22 -j ACCEPT', 0)
    ssh_client.close()
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', dport)
    exec_command(ssh_client, 'route add default gw 192.168.0.2', 0)
    ssh_client.close()


class myThread (threading.Thread):
    '''
    Subclass of Thread.
    Run function calls creat_single_hadoop
    '''
    def __init__(self, threadID, name, vm):
        threading.Thread.__init__(self)
        self.threadID = threadID  # Ranges from 1 to clustersize
        self.name = name  # Fully qualified domain name of each vm
        self.vm = vm  # member of the server list returned by create_server

    def run(self):
        logging.info("Starting %s thread", self.name)
        creat_single_hadoop_cluster(self.vm)


def create_multi_hadoop_cluster(server):
    '''
    Function that starts the threads.Creates thread objects,one for every
    virtual machine. Thread name is the fully qualified domain name of
    the virtual machine. Before the thread creation calls the
    get_ready_for_reroute to do a pre-setup for port forwarding
    in the master.
    '''
    get_ready_for_reroute()
    i = 0
    threads = []
    for s in server:
        t = myThread(i, s['SNF:fqdn'], s)
        t.start()
        threads.append(t)
        i = i+1

# Wait for all threads to complete
    for t in threads:
        t.join()


def creat_single_hadoop_cluster(s):
    '''
    Splits the threads. Master thread calls install_hadoop with port 22.
    Slave ports and slave_ips are defined by the last number in their name.
    10000 is the first slave port and 192.168.0.3 the first private slave ip.
    By adding 1 to the port and ip we have the next slave port and ip.
    There is a thread lock before reroute.That is because sometimes iptables
    fails from threads giving the command at the same time.
    The error is: resource temporarily unavailable.After the lock
    each slave thread calls install hadoop with its port.
    '''
    if s['name'].split('-')[-1] == '1':
        install_hadoop(22)
    else:
        port = 9998+int(s['name'].split('-')[-1])
        slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
        threadLock.acquire()
        reroute_ssh_to_slaves(port, slave_ip)
        threadLock.release()
        install_hadoop(port)


def exec_command(ssh, command, check_id):
    '''
    Calls paramiko exec_command function of the ssh object given
    as argument. Command is the second argument and its a string.
    check_id is used for commands that need additional input after
    exec_command, e.g. ssh-keygen needs [enter] to save keys.
    '''
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    if check_id == 1:  # For ssh-keygen
        stdin.write('\n')
        stdin.flush()
        logging.debug('%s %s',stdout.read(), stderr.read())
    elseif check_id == 2:
        sleep(3)
        stdin.write('yes\n')
        sleep(2)
        stdin.write('hduserpass\n')
        stdin.flush()
        logging.debug('%s %s', stdout.read(), stderr.read())
    else:
        logging.debug('%s %s', stdout.read(), stderr.read())
        


def install_hadoop(port):
    '''
    Function that is executed by every thread.
    Depending on the port argument, it connects
    and installs hadoop to the vm defined by the
    port.First,it connects with master as root.
    Runs apt-get update,installs sudo. Then calls 
    other important functions and disconnects as root.
    Reconnects as hduser and configures bashrc
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', port)
    exec_command(ssh_client, 'apt-get update;apt-get install sudo', 0)

    install_python_and_java(ssh_client)
    add_hduser_disable_ipv6(ssh_client)

    ssh_client.close()
    ssh_client = establish_connect(HOSTNAME_MASTER, 'hduser', 'hduserpass',
                                   port)
    connect_as_hduser_conf_ssh(ssh_client)
    configuration_bashrc(ssh_client)
    ssh_client.close()


def establish_connect(hostname, name, passwd, port):
    '''
    Establishes an ssh connection with given hostname, username, password
    and port number. If connection fails, retry for five times and then
    system exits. If a connection is succesful, returns an ssh object.
    '''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for i in range(5):
        try:
            ssh.connect(hostname, username=name, password=passwd, port=port)
            logging.info('success in connection as %s', name)
            return ssh
        except:
            logging.erroe( 'error connecting as %s', name)
    sys.exit(error_ssh_connection)


def connect_as_hduser_conf_ssh(ssh_client):
    '''
    Executes the following commands to the machine ssh_client is connected.
    Creates ssh key for hduser, downloads hadoop from eu apache mirror
    and creates hadoop folder in usr/local.
    '''
    logging.info('Start downloading hadoop.')
    exec_command(ssh_client, 'ssh-keygen -t rsa -P "" ', 1)
    exec_command(ssh_client, 'cat /home/hduser/.ssh/id_rsa.pub >> /home/'
                             'hduser/.ssh/authorized_keys', 0)
    exec_command(ssh_client, 'wget www.eu.apache.org/dist/hadoop/common/'
                             'stable1/hadoop-1.2.1.tar.gz', 0)
    exec_command(ssh_client, 'sudo tar -xzf $HOME/hadoop-1.2.1.tar.gz', 0)
    exec_command(ssh_client, 'sudo mv hadoop-1.2.1 /usr/local/hadoop', 0)
    exec_command(ssh_client, 'cd /usr/local;sudo chown -R hduser:hadoop'
                             ' hadoop', 0)
    logging.info('Done downloading hadoop.')


def install_python_and_java(ssh_client):
    '''
    Install python-software-properties
    and oracle java 7
    '''
    logging.info('start installing python and java.')
    exec_command(ssh_client, 'apt-get -y install python-software-'
                             'properties', 0)
    exec_command(ssh_client, 'echo "deb http://ppa.launchpad.net/webupd8team/'
                             'java/ubuntu precise main" | tee /etc/apt/sources'
                             '.list.d/webupd8team-java.list;echo "deb-src '
                             'http://ppa.launchpad.net/webupd8team/java/ubuntu'
                             ' precise main" | tee -a /etc/apt/sources.list.d/'
                             'webupd8team-java.list', 0)
    exec_command(ssh_client, 'apt-key adv --keyserver keyserver.ubuntu.com --'
                             'recv-keys EEA14886;apt-get update;echo oracle-'
                             'java7-installer shared/accepted-oracle-license-'
                             'v1-1 select true | /usr/bin/debconf-set-'
                             'selections;apt-get -y install oracle-java7'
                             '-installer', 0)
    exec_command(ssh_client, 'apt-get install oracle-java7-set-default', 0)
    logging.info('Done install python and java.')
    

def add_hduser_disable_ipv6(ssh_client):
    '''
    Creates hadoop group and hduser and
    gives them passwordless sudo to help with remaining procedure
    Also disables ipv6
    '''
    logging.info('Start creating hadoop group and hduser and disables ipv6.')
    exec_command(ssh_client, 'addgroup hadoop;echo "%hadoop ALL=(ALL)'
                             ' NOPASSWD: ALL " >> /etc/sudoers', 0)
    exec_command(ssh_client, 'adduser hduser --disabled-password --gecos "";'
                             'adduser hduser hadoop;echo "hduser:hduserpass" |'
                             ' chpasswd', 0)
    exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv6/conf/all/'
                             'disable_ipv6', 0)
    exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv6/conf/default/'
                             'disable_ipv6', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.all.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.default.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.lo.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)
    logging.info('Done creating hadoop group and hduser and disables ipv6.')
    

def check_credentials(auth_url, token):
    '''Identity,Account/Astakos. Test authentication credentials'''
    logging.info(' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        logging.error('Authentication failed with url %s and token %s' % (
              auth_url, token))
        raise
    logging.warning('Authentication verified')
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
    logging.info('Get the endpoints')
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
    from kamaki.clients.pithos import PithosClient

    logging.info('Initialize Pithos+ client and set account to user uuid')
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
    logging.info(' Create the container "images" and use it')
    try:
        pithos.create_container(container, success=(201, ))
    except ClientError as ce:
        if ce.status in (202, ):
            logging.error('Container %s already exists' % container)
        else:
            logging.error('Failed to create container %s' % container)
            raise
    pithos.container = container

    logging.info(' Upload to "images"')
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
    from kamaki.clients.cyclades import CycladesNetworkClient

    logging.info(' Initialize a cyclades network client')
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
    from kamaki.clients.image import ImageClient

    logging.info(' Initialize ImageClient')
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
    logging.info(' Register the image')
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
    from kamaki.clients.cyclades import CycladesClient

    logging.info(' Initialize a cyclades client')
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

    def list(self):
        '''Returns list of servers/Not used '''
        return [s for s in self.client.list_servers(detail=True) if (
            s['name'].startswith(self.prefix))]

    def clean_up(self):
        '''Deletes Cluster/Not used'''
        to_delete = self.list()
        logging.info('  There are %s servers to clean up' % len(to_delete))
        for server in to_delete:
            self.client.delete_server(server['id'])
        for server in to_delete:
            self.client.wait_server(
                server['id'], server['status'])

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
            return float_net_id[56:]
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
        dict_quotas = self.auth.get_quotas()
        limit_net = dict_quotas['system']['cyclades.network.private']['limit']
        usage_net = dict_quotas['system']['cyclades.network.private']['usage']
        pending_net = \
            dict_quotas['system']['cyclades.network.private']['pending']
        available_networks = limit_net-usage_net-pending_net
        if available_networks >= 1:
            logging.info('Private Network quota is ok')
            return
        else:
            logging.error('Private Network quota exceeded')
            sys.exit(error_quotas_netwrok)

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        '''
        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        '''
        logging.warning('\n Create %s servers prefixed as %s' 
            self.size, self.prefix)
        servers = []
        empty_ip_list = []
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s%s%s' % (date_time, '-', self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = date_time + '-' + self.prefix
        self.check_network_quota()
        # Creates network
        new_network = self.nc.create_network('MAC_FILTERED', net_name)
        # Gets list of floating ips
        list_float_ips = self.nc.list_floatingips()
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
                            logging.error('Cannot create new ip')
                            self.nc.delete_network(new_network['id'])
                            raise
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            pub_net_list = self.nc.list_networks()
            float_net_id = self.get_flo_net_id(pub_net_list)
            self.nc.create_floatingip(float_net_id)
        logging.info(' Wait for %s servers to built' % self.size)

        # Creation of master server

        servers.append(self.client.create_server(
            server_name, self.flavor_id_master, self.image_id,
            personality=self._personality(ssh_k_path, pub_k_path)))
        # Creation of slave servers
        for i in range(2, self.size+1):
            try:

                server_name = '%s%s%s%s%s' % (date_time,
                                              '-', self.prefix, '-', i)
                servers.append(self.client.create_server(
                    server_name, self.flavor_id_slave, self.image_id,
                    personality=self._personality(ssh_k_path, pub_k_path),
                    networks=empty_ip_list))

            except ClientError:
                logging.error('Failed while creating server %s' % server_name)
                raise
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        new_status = self.client.wait_server(servers[0]['id'],
                                             current_status='BUILD',
                                             delay=1, max_wait=100)
        logging.info(' Status for server %s is %s' % (
              servers[0]['name'],
              new_status))
        # We create a subnet for the virtual network between master and slaves
        # along with the ports needed
        self.nc.create_subnet(new_network['id'], '192.168.0.0/24',
                              enable_dhcp=True)
        self.nc.create_port(new_network['id'], servers[0]['id'])

        # Wait server for the slaves, so we can use their server id
        # in port creation
        for i in range(1, self.size):
            new_status = self.client.wait_server(servers[i]['id'],
                                                 current_status='BUILD',
                                                 delay=2, max_wait=100)
            logging.info(' Status for server %s is %s' % (
                servers[i]['name'], new_status))
            self.nc.create_port(new_network['id'], servers[i]['id'])

        # Not used/Left for future use
        if server_log_path:
            logging.info(' Store passwords in file %s' % server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)
        return servers


def get_flavor_id(cpu, ram, disk, disk_template, cycladesclient):
    '''Return the flavor id based on cpu,ram,disk_size and disk template'''
    flavor_list = cycladesclient.list_flavors(True)
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
    dict_quotas = auth.get_quotas()
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
        logging('Cyclades vms out of limit')
        sys.exit(error_quotas_clustersize)
    logging.warning('Cyclades Cpu,Disk and Ram quotas are ok.')
    return


def main(opts):
    '''
    The main function of our script takes the arguments given and calls the
    check_quota function. Also, calls get_flavor_id to find the matching
    flavor_ids from the arguments given and finds the image id of the
    image given as argument. Then instantiates the Cluster and creates
    the virtual machine cluster of one master and clustersize-1 slaves.
    Calls the function to install hadoop to the cluster
    '''
    logging.warning('1.  Credentials  and  Endpoints')
    # Finds user public ssh key
    USER_HOME = os.path.expanduser('~')
    pub_keys_path = os.path.join(USER_HOME, ".ssh/id_rsa.pub")
    auth = check_credentials(opts.auth_url, opts.token)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], opts.token)
    flavor_master = get_flavor_id(opts.cpu_master, opts.ram_master,
                                  opts.disk_master, opts.disk_template,
                                  cyclades)
    flavor_slaves = get_flavor_id(opts.cpu_slave, opts.ram_slave,
                                  opts.disk_slave, opts.disk_template,
                                  cyclades)
    if flavor_master == 0 or flavor_slaves == 0:
        logging.error('Combination of cpu,ram,disk and disk_template does not match'
                      ' an existing id')
        sys.exit(error_flavor_id)
    # Total cpu,ram and disk needed for cluster
    cpu = opts.cpu_master + (opts.cpu_slave)*(opts.clustersize-1)
    ram = opts.ram_master + (opts.ram_slave)*(opts.clustersize-1)
    cyclades_disk = opts.disk_master + (opts.disk_slave)*(opts.clustersize-1)
    # The resources requested by user in a dictionary
    req_quotas = {'cpu': cpu, 'ram': ram, 'cyclades_disk': cyclades_disk,
                  'vms': opts.clustersize}
    check_quota(auth, req_quotas)
    plankton = init_plankton(endpoints['plankton'], opts.token)
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the arg given
    for lst in list_current_images:
        if lst['name'] == opts.image:
            chosen_image = lst

    logging.warning('2.  Create  virtual  cluster')
    cluster = Cluster(cyclades,
                      prefix=opts.name,
                      flavor_id_master=flavor_master,
                      flavor_id_slave=flavor_slaves,
                      image_id=chosen_image['id'],
                      size=opts.clustersize,
                      net_client=init_cyclades_netclient(endpoints['network'],
                                                         opts.token),
                      auth_cl=auth)

    server = cluster.create('', pub_keys_path, '')
    logging.warning('3. Create Hadoop cluster')
    for s in server:
        if s['name'].split('-')[-1] == '1':
            # Hostname of master is used in every ssh connection.
            # So it is defined as global
            global HOSTNAME_MASTER
            HOSTNAME_MASTER = s['SNF:fqdn']

    create_multi_hadoop_cluster(server)  # Starts the hadoop installation


if __name__ == '__main__':

    #  Add some interaction candy
    from optparse import OptionParser

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

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
                      '.Default=https://accounts.okeanos.grnet.gr/identity/v2.0',
                      default='https://accounts.okeanos.grnet.gr/identity/v2.0')

    opts, args = parser.parse_args(argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    if opts.clustersize <= 0:
        logging.error('invalid syntax for clustersize'
            ',clustersize must be a positive integer')
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
        logging.error('invalid syntax for disk_template'
            ', disk_template must be drbd or ext_vlmc')
        sys.exit(error_syntax_disk_template)

    main(opts)
