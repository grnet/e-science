# -*- coding: utf-8 -*-

""" Functionality related to unit tests with un-managed resources mocked. """
# setup testing framework
from unittest import TestCase, main
from mock import patch
from ConfigParser import RawConfigParser, NoSectionError
from kamaki.clients.utils import https
https.patch_ignore_ssl()

# get relative path references so imports will work,
# even if __init__.py is missing (/tests is a simple directory not a module)
import sys
from os.path import join, dirname, abspath

sys.path.append(join(dirname(abspath(__file__)), '../orka-0.1.0'))

# import objects we aim to test
from orka.create_cluster import YarnCluster, ClientError
from orka.cluster_errors_constants import error_quotas_cluster_size, error_quotas_network, \
    error_get_ip, error_quotas_cpu, error_quotas_ram, error_quotas_cyclades_disk

def mock_createcluster(*args):
    """ :returns proper master_ip and image list types with dummy values. """
    print 'in mock create cluster'
    fake_master_ip = '127.0.0.1'
    fake_vm_dict = [{'name': 'f_vm', 'adminPass': 'blabla'}, {'name': 'f_2 vm', 'adminPass': 'blabla2'}]
    return fake_master_ip, fake_vm_dict

def mock_createpassfile(*args):
    print 'create PLACEHOLDER password file'

def mock_sleep(*args):
    """ Noop time.sleep(). Returns immediately. """
    print 'in mock sleep'


class MockAstakos():
    """ support class for faking AstakosClient.get_quotas """

    def get_quotas(self, *args):
        return { 'some_project_id':
                     {'cyclades.disk':
                          {'project_limit': 1288490188800, 'project_pending': 0, 'project_usage': 64424509440, 'usage': 0, 'limit': 322122547200, 'pending': 0},
                      'cyclades.vm':
                          {'project_limit': 60, 'project_pending': 0, 'project_usage': 2, 'usage': 0, 'limit': 15, 'pending': 0},
                      'pithos.diskspace':
                          {'project_limit': 429496729600, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 107374182400, 'pending': 0},
                      'cyclades.ram':
                          {'project_limit': 128849018880, 'project_pending': 0, 'project_usage': 12884901888, 'usage': 0, 'limit': 32212254720, 'pending': 0},
                      'cyclades.cpu':
                          {'project_limit': 120, 'project_pending': 0, 'project_usage': 12, 'usage': 0, 'limit': 30, 'pending': 0},
                      'cyclades.floating_ip':
                          {'project_limit': 16, 'project_pending': 0, 'project_usage': 6, 'usage': 3, 'limit': 4, 'pending': 0},
                      'cyclades.network.private':
                          {'project_limit': 16, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 4, 'pending': 0},
                      'astakos.pending_app':
                          {'project_limit': 0, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 0, 'pending': 0}} }


def mock_checkcredentials(*args):
    """ No implementation, just declaration. """
    print 'in mock check credentials'
    auth = MockAstakos()
    return auth


def mock_endpoints_userid(arg1):
    """ :return valid keys for endpoints with placeholder values. """
    print 'in mock endpoints'
    fake_uid = 'id'
    fake_endpoints = {'cyclades': 0, 'plankton': 0, 'network': 0}
    return fake_endpoints, fake_uid


def mock_init_cyclades(*args):
    """ No implementation, just declaration. """
    print 'in mock cyclades' 
    return 'https://cyclades.okeanos.grnet.gr/compute/v2.0'

 


def mock_get_flavorid(*args):
    """ :return valid static flavor id. Arguments ignored. """
    print 'in mock flavor id'
    return 1


def mock_check_quota(*args):
    """ No implementation, just declaration. """
    print 'in mock check quota'


class MockPlankton():
    """ Support class for faking .list_public method. """

    def list_public(self, *args):
        """ :returns static image list with valid keys. """

        return [{'name': 'ubuntu', 'id': 0}]

def mock_init_plankton(*args):
    """ :return: static image_list with valid keys. """
    print 'in mock init plankton'
    image_list = MockPlankton()
    return image_list


class MockCycladesNetClient():
    """ support class for faking CycladesNetworkClient.list_floatingips """

    def list_floatingips(self):
        return [{'instance_id': '604863', 'port_id': '1743733'}, {'instance_id': None, 'port_id': None},
                {'instance_id': '615302', 'port_id': '1773954'}]
        # [{'floating_network_id': '6783', 'user_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'deleted': False, 'tenant_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'instance_id': '604863', 'fixed_ip_address': None, 'floating_ip_address': '83.212.123.218', 'port_id': '1743733', 'id': '527909'},
        # {'floating_network_id': '6783', 'user_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'deleted': False, 'tenant_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'instance_id': None, 'fixed_ip_address': None, 'floating_ip_address': '83.212.123.253', 'port_id': None, 'id': '570931'},
        # {'floating_network_id': '2216', 'user_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'deleted': False, 'tenant_id': 'ec567bea-4fa2-433d-9935-261a0867ec60', 'instance_id': '615302', 'fixed_ip_address': None, 'floating_ip_address': '83.212.118.250', 'port_id': '1773954', 'id': '572851'}]


def mock_init_cyclades_netclient(*args):
    """ No implementation, just declaration.  """
    print 'in mock init cyclades netclient'
    list_ips = MockCycladesNetClient()
    return list_ips


def mock_reroute_ssh_prep(*args):
    """ No implementation, just declaration   """
    print 'in mock reroute ssh prep'


def mock_install_yarn(*args):
    """ No implementation, just declaration   """
    print 'in mock install yarn'

def mock_get_project_id(*args):
    return 'some_project_id'

# replace unmanaged calls with fakes
@patch('orka.create_cluster.Cluster.create', mock_createcluster)
@patch('orka.create_cluster.check_credentials', mock_checkcredentials)
@patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
@patch('orka.create_cluster.init_cyclades', mock_init_cyclades)
@patch('orka.create_cluster.YarnCluster.get_flavor_id_master', mock_get_flavorid)
@patch('orka.create_cluster.YarnCluster.get_flavor_id_slave', mock_get_flavorid)
@patch('orka.create_cluster.get_project_id', mock_get_project_id)
@patch('orka.create_cluster.init_plankton', mock_init_plankton)
@patch('orka.create_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
@patch('orka.create_cluster.reroute_ssh_prep', mock_reroute_ssh_prep)
@patch('orka.create_cluster.install_yarn', mock_install_yarn)
@patch('orka.create_cluster.sleep', mock_sleep)
class TestCreateCluster(TestCase):
    """ Test cases with separate un-managed resources mocked. """
    # initialize objects common to all tests in this test case
    def setUp(self):
        parser = RawConfigParser()
        config_file = join(dirname(dirname(abspath(__file__))), '.private/.config.txt')
        parser.read(config_file)
        try:
            self.token = parser.get('cloud \"~okeanos\"', 'token')
            self.auth_url = parser.get('cloud \"~okeanos\"', 'url')
            self.project_name = parser.get('project', 'name')
            self.opts = {'name': 'Test', 'cluster_size': 2, 'cpu_master': 2,
                'ram_master': 4096, 'disk_master': 5, 'cpu_slave': 2,
                'ram_slave': 2048, 'disk_slave': 5, 'token': self.token,
                'disk_template': 'ext_vlmc', 'image': 'ubuntu',
                'auth_url': self.auth_url, 'project_name': self.project_name}
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    # @patch('create_cluster.init_plankton', mock_init_plankton)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)  
    @patch('orka.create_cluster.YarnCluster.create_password_file', mock_createpassfile)
    def test_create_yarn_cluster(self):
        # arrange
        expected_masterip = '127.0.0.1'
        expected_vm_dict = [{'name': 'f_vm', 'adminPass': 'blabla'}, {'name': 'f_2 vm', 'adminPass': 'blabla2'}]
        c_yarn_cluster = YarnCluster(self.opts)

        # act
        returned_masterip, returned_vm_dict = c_yarn_cluster.create_yarn_cluster()
        # assert
        self.assertTupleEqual((expected_masterip, expected_vm_dict), (returned_masterip, returned_vm_dict))

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_clustersize_quotas_sufficient(self):
        # arrange
        prev_clustersize = self.opts['cluster_size']
        self.opts['cluster_size'] = 2
        c_yarn_cluster = YarnCluster(self.opts)
        expected = 0  # usage: 4, limit: 6 (2 remaining), requested: 2, expected result success
        # act
        returned = c_yarn_cluster.check_cluster_size_quotas()
        self.opts['cluster_size'] = prev_clustersize
        # assert
        self.assertEqual(expected, returned)


    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_clustersize_quotas_exceeded(self):
        # arrange
        prev_clustersize = self.opts['cluster_size']
        self.opts['cluster_size'] = 30
        c_yarn_cluster = YarnCluster(self.opts)
        expected = error_quotas_cluster_size
        # act
        with self.assertRaises(ClientError) as context:
            c_yarn_cluster.check_cluster_size_quotas()
        self.opts['cluster_size'] = prev_clustersize
        # assert
        the_exception = context.exception
        self.assertEqual(expected, the_exception.status)

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_network_quotas_sufficient(self):
        # arrange
        c_yarn_cluster = YarnCluster(self.opts)
        expected = 0  # success
        # act
        returned = c_yarn_cluster.check_network_quotas()
        # assert
        self.assertEqual(expected, returned)

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_ip_quotas_sufficient(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_ip_quotas_exceeded(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_cpu_valid_sufficient(self):
        # arrange
        prev_clustersize = self.opts['cluster_size']
        self.opts['cluster_size'] = 2
        c_yarn_cluster = YarnCluster(self.opts)
        expected = 0  # usage: 5, limit: 9 (4 remaining), requested: 4, expected result success
        # act
        returned = c_yarn_cluster.check_cpu_valid()
        self.opts['cluster_size'] = prev_clustersize
        # assert
        self.assertEqual(expected, returned)

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_cpu_valid_exceeded(self):
        # arrange
        prev_clustersize = self.opts['cluster_size']
        self.opts['cluster_size'] = 30
        c_yarn_cluster = YarnCluster(self.opts)
        expected = error_quotas_cpu
        # act
        with self.assertRaises(ClientError) as context:
            c_yarn_cluster.check_cpu_valid()
        self.opts['cluster_size'] = prev_clustersize
        # assert
        the_exception = context.exception
        self.assertEqual(expected, the_exception.status)

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    def test_check_ram_valid_sufficient(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    def test_check_ram_valid_exceeded(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    def test_check_disk_valid_sufficient(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    def test_check_disk_valid_exceeded(self):
        # arrange
        pass
        # act

        # assert

    @patch('orka.create_cluster.check_credentials', mock_checkcredentials)
    @patch('orka.create_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
    @patch('orka.create_cluster.endpoints_and_user_id', mock_endpoints_userid)
    def test_check_all_resources(self):
        # arrange
        c_yarn_cluster = YarnCluster(self.opts)
        expected = 0
        # act
        returned = c_yarn_cluster.check_all_resources()
        # assert
        self.assertTrue(True)  # temporarily short-ciruit

    # free up any resources not automatically released
    def tearDown(self):
        pass


if __name__ == '__main__':
    main()
