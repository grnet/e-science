from sys import argv
from os.path import abspath
from base64 import b64encode
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from datetime import datetime
import os
import nose
#  Identity,Account / Astakos
#  Test authentication credentials


def check_credentials(auth_url, token):

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

#  Get the endpoints
#  Identity, Account --> astakos
#  Compute --> cyclades
#  Object-store --> pithos
#  Image --> plankton
#  Network --> network


def endpoints_and_user_id(auth):

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

#  Object-store / Pithos+/ Not used in the script,but left for future use


def init_pithos(endpoint, token, user_id):
    from kamaki.clients.pithos import PithosClient

    print(' Initialize Pithos+ client and set account to user uuid')
    try:
        return PithosClient(endpoint, token, user_id)
    except ClientError:
        print('Failed to initialize a Pithos+ client')
        raise

# Pithos+/Upload Image/ Not used in the script,but left for future use


def upload_image(pithos, container, image_path):

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

# Initialize CycladesNetworkClient/ Cyclades Network client needed for all
#  network functions e.g. create network,create floating ip


def init_cyclades_netclient(endpoint, token):
    from kamaki.clients.cyclades import CycladesNetworkClient

    print(' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        print('Failed to initialize cyclades network client')
        raise

#  Plankton/Initialize Imageclient/ImageClient has all registered images


def init_plankton(endpoint, token):
    from kamaki.clients.image import ImageClient

    print(' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        print('Failed to initialize the Image client')
        raise

# Image/Plankton/Registers image from Pithos in Plankton/Not used
# but left for future use


def register_image(plankton, name, user_id, container, path, properties):

    image_location = (user_id, container, path)
    print(' Register the image')
    try:
        return plankton.register(name, image_location, properties)
    except ClientError:
        print('Failed to register image %s' % name)
        raise

#  Compute / Initialize Cyclades client/CycladesClient is used
#  to create virtual machines


def init_cyclades(endpoint, token):
    from kamaki.clients.cyclades import CycladesClient

    print(' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        print('Failed to initialize cyclades client')
        raise

# Cluster class represents an entire cluster.Instantiation of cluster gets
# the following arguments: A CycladesClient object,a name-prefix for the
# cluster,the flavors of master and slave machines,the image id of their OS,
# the size of the cluster,a CycladesNetworkClient object and a AstakosClient
# object.


class Cluster(object):

    def __init__(self, cyclades, prefix, flavor_id_master, flavor_id_slave,
                 image_id, size, net_client, auth_cl):
        self.client = cyclades
        self.nc = net_client
        self.prefix, self.size = prefix, int(size)
        self.flavor_id_master, self.auth = flavor_id_master, auth_cl
        self.flavor_id_slave, self.image_id = flavor_id_slave, image_id

# Returns list of servers/Not used

    def list(self):

        return [s for s in self.client.list_servers(detail=True) if (
            s['name'].startswith(self.prefix))]

# Deletes Cluster/Not used

    def clean_up(self):

        to_delete = self.list()
        print('  There are %s servers to clean up' % len(to_delete))
        for server in to_delete:
            self.client.delete_server(server['id'])
        for server in to_delete:
            self.client.wait_server(
                server['id'], server['status'])

# Gets an Ipv4 floating network id from the list of public networks Ipv4
# and Ipv6. Takes the href value and removes first 56 characters.
# The number that is left is the public network id

    def get_flo_net_id(self, list_public_networks):

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

# Personality injects ssh keys to the virtual machines we create

    def _personality(self, ssh_keys_path='', pub_keys_path=''):
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

# Checks if the user quota is enough to create a new private network
# Subtracts the number of networks used and pending from the max allowed
# number of networks

    def check_network_quota(self):

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

# Creates a cluster of virtual machines using the Create_server method of
# CycladesClient.

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
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

# Return the flavor id based on cpu,ram,disk_size and disk template


def get_flavor_id(C, R, D, disk_template):
    error = '0'
    A = range(336)
    A[0] = '46'
    A[1] = '47'
    A[2] = '48'
    A[3] = '49'
    A[4] = '50'
    A[5] = '51'
    A[6] = '52'
    A[7] = '28'
    A[8] = '29'
    A[9] = '1'
    A[10] = '3'
    A[11] = '53'
    A[12] = '54'
    A[13] = '55'
    A[14] = '30'
    A[15] = '31'
    A[16] = '4'
    A[17] = '6'
    A[18] = '56'
    A[19] = '57'
    A[20] = '58'
    A[21] = '32'
    A[22] = '33'
    A[23] = '7'
    A[24] = '9'
    A[25] = '59'
    A[26] = '60'
    A[27] = '61'
    A[28] = '306'
    A[29] = '307'
    A[30] = '308'
    A[31] = '309'
    A[32] = '310'
    A[33] = '311'
    A[34] = '290'
    A[35] = '62'
    A[36] = '63'
    A[37] = '64'
    A[38] = '65'
    A[39] = '66'
    A[40] = '67'
    A[41] = '68'
    A[42] = '69'
    A[43] = '70'
    A[44] = '71'
    A[45] = '72'
    A[46] = '73'
    A[47] = '74'
    A[48] = '75'
    A[49] = '34'
    A[50] = '35'
    A[51] = '10'
    A[52] = '12'
    A[53] = '76'
    A[54] = '77'
    A[55] = '78'
    A[56] = '36'
    A[57] = '37'
    A[58] = '13'
    A[59] = '15'
    A[60] = '79'
    A[61] = '80'
    A[62] = '81'
    A[63] = '38'
    A[64] = '39'
    A[65] = '16'
    A[66] = '18'
    A[67] = '82'
    A[68] = '83'
    A[69] = '84'
    A[70] = '315'
    A[71] = '316'
    A[72] = '317'
    A[73] = '296'
    A[74] = '295'
    A[75] = '294'
    A[76] = '293'
    A[77] = '85'
    A[78] = '86'
    A[79] = '87'
    A[80] = '88'
    A[81] = '89'
    A[82] = '90'
    A[83] = '91'
    A[84] = '92'
    A[85] = '93'
    A[86] = '94'
    A[87] = '95'
    A[88] = '96'
    A[89] = '97'
    A[90] = '98'
    A[91] = '40'
    A[92] = '41'
    A[93] = '19'
    A[94] = '21'
    A[95] = '99'
    A[96] = '100'
    A[97] = '101'
    A[98] = '42'
    A[99] = '43'
    A[100] = '22'
    A[101] = '24'
    A[102] = '102'
    A[103] = '103'
    A[104] = '104'
    A[105] = '44'
    A[106] = '45'
    A[107] = '25'
    A[108] = '27'
    A[109] = '105'
    A[110] = '106'
    A[111] = '107'
    A[112] = '325'
    A[113] = '326'
    A[114] = '327'
    A[115] = '328'
    A[116] = '329'
    A[117] = '330'
    A[118] = '331'
    A[119] = '108'
    A[120] = '109'
    A[121] = '110'
    A[122] = '111'
    A[123] = '112'
    A[124] = '113'
    A[125] = '114'
    A[126] = '115'
    A[127] = '116'
    A[128] = '117'
    A[129] = '118'
    A[130] = '119'
    A[131] = '120'
    A[132] = '121'
    A[133] = '122'
    A[134] = '123'
    A[135] = '124'
    A[136] = '125'
    A[137] = '126'
    A[138] = '127'
    A[139] = '128'
    A[140] = '129'
    A[141] = '130'
    A[142] = '131'
    A[143] = '132'
    A[144] = '133'
    A[145] = '134'
    A[146] = '135'
    A[147] = '136'
    A[148] = '137'
    A[149] = '138'
    A[150] = '139'
    A[151] = '140'
    A[152] = '141'
    A[153] = '142'
    A[154] = '339'
    A[155] = '340'
    A[156] = '341'
    A[157] = '342'
    A[158] = '343'
    A[159] = '344'
    A[160] = '345'
    A[161] = '143'
    A[162] = '144'
    A[163] = '145'
    A[164] = '146'
    A[165] = '147'
    A[166] = '148'
    A[167] = '149'
    A[168] = '150'
    A[169] = '151'
    A[170] = '152'
    A[171] = '153'
    A[172] = '154'
    A[173] = '155'
    A[174] = '156'
    A[175] = '157'
    A[176] = '158'
    A[177] = '159'
    A[178] = '160'
    A[179] = '161'
    A[180] = '162'
    A[181] = '163'
    A[182] = '164'
    A[183] = '165'
    A[184] = '166'
    A[185] = '167'
    A[186] = '168'
    A[187] = '169'
    A[188] = '170'
    A[189] = '171'
    A[190] = '172'
    A[191] = '173'
    A[192] = '174'
    A[193] = '175'
    A[194] = '176'
    A[195] = '177'
    A[196] = '300'
    A[197] = '301'
    A[198] = '302'
    A[199] = '303'
    A[200] = '304'
    A[201] = '305'
    A[202] = '291'
    A[203] = '178'
    A[204] = '179'
    A[205] = '180'
    A[206] = '181'
    A[207] = '182'
    A[208] = '183'
    A[209] = '184'
    A[210] = '185'
    A[211] = '186'
    A[212] = '187'
    A[213] = '188'
    A[214] = '189'
    A[215] = '190'
    A[216] = '191'
    A[217] = '192'
    A[218] = '193'
    A[219] = '194'
    A[220] = '195'
    A[221] = '196'
    A[222] = '197'
    A[223] = '198'
    A[224] = '199'
    A[225] = '200'
    A[226] = '201'
    A[227] = '202'
    A[228] = '203'
    A[229] = '204'
    A[230] = '205'
    A[231] = '206'
    A[232] = '207'
    A[233] = '208'
    A[234] = '209'
    A[235] = '210'
    A[236] = '211'
    A[237] = '212'
    A[238] = '312'
    A[239] = '313'
    A[240] = '314'
    A[241] = '297'
    A[242] = '298'
    A[243] = '299'
    A[244] = '292'
    A[245] = '213'
    A[246] = '214'
    A[247] = '215'
    A[248] = '216'
    A[249] = '217'
    A[250] = '218'
    A[251] = '219'
    A[252] = '220'
    A[253] = '221'
    A[254] = '222'
    A[255] = '223'
    A[256] = '224'
    A[257] = '225'
    A[258] = '226'
    A[259] = '227'
    A[260] = '228'
    A[261] = '229'
    A[262] = '230'
    A[263] = '231'
    A[264] = '232'
    A[265] = '233'
    A[266] = '234'
    A[267] = '235'
    A[268] = '236'
    A[269] = '237'
    A[270] = '238'
    A[271] = '239'
    A[272] = '240'
    A[273] = '241'
    A[274] = '242'
    A[275] = '243'
    A[276] = '244'
    A[277] = '245'
    A[278] = '246'
    A[279] = '247'
    A[280] = '318'
    A[281] = '319'
    A[282] = '320'
    A[283] = '321'
    A[284] = '322'
    A[285] = '323'
    A[286] = '324'
    A[287] = '248'
    A[288] = '249'
    A[289] = '250'
    A[290] = '251'
    A[291] = '252'
    A[292] = '253'
    A[293] = '254'
    A[294] = '255'
    A[295] = '256'
    A[296] = '257'
    A[297] = '258'
    A[298] = '259'
    A[299] = '260'
    A[300] = '261'
    A[301] = '262'
    A[302] = '263'
    A[303] = '264'
    A[304] = '265'
    A[305] = '266'
    A[306] = '267'
    A[307] = '268'
    A[308] = '269'
    A[309] = '270'
    A[310] = '271'
    A[311] = '272'
    A[312] = '273'
    A[313] = '274'
    A[314] = '275'
    A[315] = '276'
    A[316] = '277'
    A[317] = '278'
    A[318] = '279'
    A[319] = '280'
    A[320] = '281'
    A[321] = '282'
    A[322] = '332'
    A[323] = '333'
    A[324] = '334'
    A[325] = '335'
    A[326] = '336'
    A[327] = '337'
    A[328] = '338'
    A[329] = '283'
    A[330] = '284'
    A[331] = '285'
    A[332] = '286'
    A[333] = '287'
    A[334] = '288'
    A[335] = '289'

# Checks if user input is one of the fixed possibilities

    if C == 1:
        C_no = 0
    elif C == 2:
        C_no = 1
    elif C == 4:
        C_no = 2
    elif C == 8:
        C_no = 3
    else:
        return error

    if R == 512:
        R_no = 0
    elif R == 1024:
        R_no = 1
    elif R == 2048:
        R_no = 2
    elif R == 4096:
        R_no = 3
    elif R == 6144:
        R_no = 4
    elif R == 8192:
        R_no = 5
    else:
        return error

    if D == 5:
        D_no = 0
    elif D == 10:
        D_no = 1
    elif D == 20:
        D_no = 2
    elif D == 40:
        D_no = 3
    elif D == 60:
        D_no = 4
    elif D == 80:
        D_no = 5
    elif D == 100:
        D_no = 6
    else:
        return error
    if disk_template == 'drbd':
        disk_template_no = 0
    elif disk_template == 'ext_vlmc':
        disk_template_no = 1
    else:
        return error

# Produce a code from inputs to generate a code corresponding to the matching
# flavor_id on table A

    code = disk_template_no * 168+C_no * 42+R_no * 7+D_no
    return A[code]

def test_get_flavor_id():
    """get_flavor_id correct responses"""
    assert get_flavor_id(1,2048,5,'drbd') == '30'
    assert get_flavor_id(1,2048,5,'ext_vlmc') == '164'


# Checks if user's quotas are enough for what he needed to create the cluster.
# If limit minus (used and pending) are lower or
# higher than what user requests..Also divides with 1024*1024*1024 to transform
# bytes to gigabytes.


def check_quota(auth, req_quotas):

    dict_quotas = auth.get_quotas()
    limit_cd = dict_quotas['system']['cyclades.disk']['limit']
    usage_cd = dict_quotas['system']['cyclades.disk']['usage']
    pending_cd = dict_quotas['system']['cyclades.disk']['pending']
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd) / (1073741824)
    if available_cyclades_disk_GB >= req_quotas['cyclades_disk']:
        pass
    else:
        print 'Cyclades disk out of limit'
        return

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
    available_ram = (limit_ram-usage_ram-pending_ram) / (1048576)
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

# The main function of our script takes the arguments given and calls the
# check_quota function. Also, calls get_flavor_id to find the matching
# flavor_ids from the arguments given and finds the image id of the
# image given as argument. Then instantiates the Cluster and creates
# the cluster


def main(opts):

    print('1.  Credentials  and  Endpoints')
    # Finds user public ssh key
    USER_HOME = os.path.expanduser('~')
    pub_keys_path = os.path.join(USER_HOME, ".ssh/id_rsa.pub")
    auth = check_credentials(opts.auth_url, opts.token)
    endpoints, user_id = endpoints_and_user_id(auth)

    flavor_master = int(get_flavor_id(opts.cpu_master, opts.ram_master,
                                      opts.disk_master, opts.disk_template))
    flavor_slaves = int(get_flavor_id(opts.cpu_slave, opts.ram_slave,
                                      opts.disk_slave, opts.disk_template))
    if flavor_master == 0 or flavor_slaves == 0:
        print 'Wrong inputs for virtual machine hardware'
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
    cluster = Cluster(cyclades=init_cyclades(
                      endpoints['cyclades'], opts.token),
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
                      help='The name to use for naming cluster nodes',
                      default='cluster')
    parser.add_option('--clustersize',
                      action='store', type='int', dest='clustersize',
                      help='Number of virtual cluster nodes to create ',
                      default=2)
    parser.add_option('--cpu_master',
                      action='store', type='int', dest='cpu_master',
                      metavar='CPU MASTER',
                      help='Choose number of cores for the virtual hardware '
                           'of master node',
                      default=2)
    parser.add_option('--ram_master',
                      action='store', type='int', dest='ram_master',
                      metavar='RAM MASTER',
                      help='Choose size of ram for the virtual hardware '
                           'of master node',
                      default=2048)
    parser.add_option('--disk_master',
                      action='store', type='int', dest='disk_master',
                      metavar='DISK MASTER',
                      help='Choose disk size for the virtual hardware '
                           'of master node',
                      default=10)
    parser.add_option('--disk_template',
                      action='store', type='string', dest='disk_template',
                      metavar='DISK TEMPLATE',
                      help='Choose disk template between drbd and ext_vlmc',
                      default='ext_vlmc')
    parser.add_option('--cpu_slave',
                      action='store', type='int', dest='cpu_slave',
                      metavar='CPU SLAVE',
                      help='Choose number of cores for the virtual hardware '
                           'of slave nodes',
                      default=2)
    parser.add_option('--ram_slave',
                      action='store', type='int', dest='ram_slave',
                      metavar='RAM SLAVE',
                      help='Choose size of ram for the virtual hardware '
                           'of slave nodes',
                      default=1024)
    parser.add_option('--disk_slave',
                      action='store', type='int', dest='disk_slave',
                      metavar='DISK SLAVE',
                      help='Choose disk size for the virtual hardware '
                           'of slave nodes',
                      default=10)
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='token',
                      help='Insert token for authentication',
                      default='37cnXlDd1T4VfIsWRtXhaV-iE_2c2_gmiM40gVk3JSs')
    parser.add_option('--image',
                      action='store', type='string', dest='image',
                      metavar='IMAGE OS',
                      help='Choose OS for the virtual machine cluster',
                      default='Debian Base')

    parser.add_option('--auth_url',
                      action='store', type='string', dest='auth_url',
                      metavar='AUTHENTICATION URL',
                      help='Insert authentication url',
                      default='https://accounts.okeanos.grnet.gr/identity/v2.0'
                      )

    opts, args = parser.parse_args(argv[1:])
    main(opts)
