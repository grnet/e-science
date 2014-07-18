import sys
from sys import argv
from os.path import abspath
from base64 import b64encode
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from datetime import datetime
import os
import nose

Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes


def check_credentials(auth_url, token):
    '''Identity,Account/Astakos. Test authentication credentials'''
    print(' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        print('Authentication failed with url %s and token %s' % (
              auth_url, token))
        raise
    print 'Authentication verified'
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
    print(' Get the endpoints')
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
        print('Failed to get endpoints & user_id from identity server')
        raise
    return endpoints, user_id


def init_pithos(endpoint, token, user_id):
    '''
    Object-store / Pithos+.Not used in the script,
    but left for future use
    '''
    from kamaki.clients.pithos import PithosClient

    print(' Initialize Pithos+ client and set account to user uuid')
    try:
        return PithosClient(endpoint, token, user_id)
    except ClientError:
        print('Failed to initialize a Pithos+ client')
        raise


def upload_image(pithos, container, image_path):
    '''

    Pithos+/Upload Image
    Not used in the script,but left for future use
    '''
    print(' Create the container "images" and use it')
    try:
        pithos.create_container(container, success=(201, ))
    except ClientError as ce:
        if ce.status in (202, ):
            print('Container %s already exists' % container)
        else:
            print('Failed to create container %s' % container)
            raise
    pithos.container = container

    print(' Upload to "images"')
    with open(abspath(image_path)) as f:
        try:
            pithos.upload_object(
                image_path, f)
        except ClientError:
            print('Failed to upload file %s to container %s' % (
                image_path, container))
            raise


def init_cyclades_netclient(endpoint, token):
    '''

    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating ip
    '''
    from kamaki.clients.cyclades import CycladesNetworkClient

    print(' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        print('Failed to initialize cyclades network client')
        raise


def init_plankton(endpoint, token):
    '''

    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    '''
    from kamaki.clients.image import ImageClient

    print(' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        print('Failed to initialize the Image client')
        raise


def register_image(plankton, name, user_id, container, path, properties):
    '''

    Image/Plankton.Registers image from Pithos in Plankton.Not used
    but left for future use
    '''
    image_location = (user_id, container, path)
    print(' Register the image')
    try:
        return plankton.register(name, image_location, properties)
    except ClientError:
        print('Failed to register image %s' % name)
        raise


def init_cyclades(endpoint, token):
    '''

    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    '''
    from kamaki.clients.cyclades import CycladesClient

    print(' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        print('Failed to initialize cyclades client')
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
        print('  There are %s servers to clean up' % len(to_delete))
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
            print 'Floating Network Id could not be found'
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
            print 'Private Network quota is ok'
            return 1
        else:
            print 'Private Network quota exceeded'
            return 0

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        '''

        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        '''
        print('\n Create %s servers prefixed as %s' % (
            self.size, self.prefix))
        servers = []
        empty_ip_list = []
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s%s%s' % (date_time, '-', self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = date_time + '-' + self.prefix
        # Checks network creation quota, if it returns 0
        # the create function terminates
        net_check = self.check_network_quota()
        if(net_check == 0):
            return
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
                            print('Cannot create new ip')
                            self.nc.delete_network(new_network['id'])
                            raise
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            pub_net_list = self.nc.list_networks()
            float_net_id = self.get_flo_net_id(pub_net_list)
            self.nc.create_floatingip(float_net_id)
        print(' Wait for %s servers to built' % self.size)

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
                print('Failed while creating server %s' % server_name)
                raise
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        new_status = self.client.wait_server(servers[0]['id'],
                                             current_status='BUILD',
                                             delay=1, max_wait=100)
        print(' Status for server %s is %s' % (
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
            print(' Status for server %s is %s' % (
                servers[i]['name'], new_status))
            self.nc.create_port(new_network['id'], servers[i]['id'])

        # Not used/Left for future use
        if server_log_path:
            print(' Store passwords in file %s' % server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)

        return servers


def get_flavor_id(cpu, ram, disk, disk_template, cycladesclient):
    '''Return the flavor id based on cpu,ram,disk_size and disk template'''
    flavor_list = cycladesclient.list_flavors(True)
    flavor_id = 0
    for flavor in flavor_list:
        if flavor['ram'] == ram and flavor['SNF:disk_template'] == \
            disk_template and flavor['vcpus'] \
                == cpu and flavor['disk'] == disk:
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
    if available_cyclades_disk_GB >= req_quotas['cyclades_disk']:
        pass
    else:
        print 'Cyclades disk out of limit'
        return 0

    limit_cpu = dict_quotas['system']['cyclades.cpu']['limit']
    usage_cpu = dict_quotas['system']['cyclades.cpu']['usage']
    pending_cpu = dict_quotas['system']['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu
    if available_cpu >= req_quotas['cpu']:
        pass
    else:
        print 'Cyclades cpu out of limit'
        return 0

    limit_ram = dict_quotas['system']['cyclades.ram']['limit']
    usage_ram = dict_quotas['system']['cyclades.ram']['usage']
    pending_ram = dict_quotas['system']['cyclades.ram']['pending']
    available_ram = (limit_ram-usage_ram-pending_ram) / Bytes_to_MB
    if available_ram >= req_quotas['ram']:
        pass
    else:
        print 'Cyclades ram out of limit'
        return 0
    limit_vm = dict_quotas['system']['cyclades.vm']['limit']
    usage_vm = dict_quotas['system']['cyclades.vm']['usage']
    pending_vm = dict_quotas['system']['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm
    if available_vm >= req_quotas['vms']:
        pass
    else:
        print 'Cyclades vms out of limit'
        return 0
    print 'Cyclades Cpu,Disk and Ram quotas are ok.'
    return 1


def main(opts):
    '''

    The main function of our script takes the arguments given and calls the
    check_quota function. Also, calls get_flavor_id to find the matching
    flavor_ids from the arguments given and finds the image id of the
    image given as argument. Then instantiates the Cluster and creates
    the virtual machine cluster of one master and clustersize-1 slaves.
    '''
    print('1.  Credentials  and  Endpoints')
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
        print 'Combination of cpu,ram,disk and disk_template does not match'\
            ' an existing id'
        return
    # Total cpu,ram and disk needed for cluster
    cpu = opts.cpu_master + (opts.cpu_slave)*(opts.clustersize-1)
    ram = opts.ram_master + (opts.ram_slave)*(opts.clustersize-1)
    cyclades_disk = opts.disk_master + (opts.disk_slave)*(opts.clustersize-1)
    # The resources requested by user in a dictionary
    req_quotas = {'cpu': cpu, 'ram': ram, 'cyclades_disk': cyclades_disk,
                  'vms': opts.clustersize}
    k = check_quota(auth, req_quotas)
    # If check_quota returns 0 main ends
    if k == 0:
        return
    plankton = init_plankton(endpoints['plankton'], opts.token)
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the arg given
    for lst in list_current_images:
        if lst['name'] == opts.image:
            chosen_image = lst

    print('2.  Create  virtual  cluster')
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
                      help='Synnefo authentication url')

    opts, args = parser.parse_args(argv[1:])

    if opts.clustersize > 0:
        pass
    else:
        print 'invalid syntax for opts.clustersize'\
            ',opts.clustersize must be a positive integer'
        sys.exit(0)

    if opts.cpu_master > 0:
        pass
    else:
        print 'invalid syntax for cpu_master'\
            ', cpu_master must be a positive integer'
        sys.exit(0)

    if opts.ram_master > 0:
        pass
    else:
        print 'invalid syntax for ram_master'\
            ', ram_master must be a positive integer'
        sys.exit(0)

    if opts.disk_master > 0:
        pass
    else:
        print 'invalid syntax for disk_master'\
            ', disk_master must be a positive integer'
        sys.exit(0)

    if opts.cpu_slave > 0:
        pass
    else:
        print 'invalid syntax for cpu_slave'\
            ', cpu_slave must be a positive integer'
        sys.exit(0)

    if opts.ram_slave > 0:
        pass
    else:
        print 'invalid syntax for ram_slave'\
            ', ram_slave must be a positive integer'
        sys.exit(0)

    if opts.disk_slave > 0:
        pass
    else:
        print 'invalid syntax for disk_slave'\
            ', disk_slave must be a positive integer'
        sys.exit(0)

    main(opts)

