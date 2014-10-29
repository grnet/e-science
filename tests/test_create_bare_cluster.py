# -*- coding: utf-8 -*-

""" Functionality related to unit tests with un-managed resources mocked. """
# setup testing framework
from unittest import TestCase, main
from mock import patch
from ConfigParser import RawConfigParser, NoSectionError

# get relative path references so imports will work,
# even if __init__.py is missing (/tests is a simple directory not a module)
import sys
from os.path import join, dirname, abspath

sys.path.append(join(dirname(__file__), '..'))

# import objects we aim to test
from create_bare_cluster import create_cluster


def mock_createcluster(*args):
    """ :returns proper master_ip and image list types with dummy values. """
    print 'in mock create cluster'
    fake_master_ip = '127.0.0.1'
    fake_vm_dict = {1: 'f vm'}
    return fake_master_ip, fake_vm_dict


def mock_sleep(*args):
    """ Noop time.sleep(). Returns immediately. """
    print 'in mock sleep'


def mock_checkcredentials(*args):
    """ No implementation, just declaration. """
    print 'in mock check credentials'


def mock_endpoints_userid(arg1):
    """ :return valid keys for endpoints with placeholder values. """
    print 'in mock endpoints'
    fake_uid = 'id'
    fake_endpoints = {'cyclades': 0, 'plankton': 0, 'network': 0}
    return fake_endpoints, fake_uid


def mock_init_cyclades(*args):
    """ No implementation, just declaration. """
    print 'in mock cyclades'


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
        return [{'name': 'Debian Base', 'id': 0}]


def mock_init_plankton(*args):
    """ :return: static image_list with valid keys. """
    print 'in mock init plankton'
    image_list = MockPlankton()
    return image_list


def mock_init_cyclades_netclient(*args):
    """ No implementation, just declaration.  """
    print 'in mock init cyclades netclient'


# replace unmanaged calls with the mocks
@patch('create_bare_cluster.Cluster.create', mock_createcluster)
# @patch('create_bare_cluster.check_credentials', mock_checkcredentials)
# @patch('create_bare_cluster.endpoints_and_user_id', mock_endpoints_userid)
# @patch('create_bare_cluster.init_cyclades', mock_init_cyclades)
# @patch('create_bare_cluster.get_flavor_id', mock_get_flavorid)
# @patch('create_bare_cluster.check_quota', mock_check_quota)
# @patch('create_bare_cluster.init_plankton', mock_init_plankton)
# @patch('create_bare_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
@patch('create_bare_cluster.sleep', mock_sleep)
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
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    def test_create_cluster(self):
        # arrange
        opts = {'name': 'Test', 'clustersize': 2, 'cpu_master': 2,
                'ram_master': 4096, 'disk_master': 5, 'cpu_slave': 2,
                'ram_slave': 2048, 'disk_slave': 5, 'token': self.token,
                'disk_template': 'ext_vlmc', 'image': 'Debian Base',
                'auth_url': self.auth_url}
        expected_masterip = '127.0.0.1'
        expected_vm_dict = {1: 'f vm'}
        # act
        returned_masterip, returned_vm_dict = create_cluster(**opts)
        # assert
        self.assertTupleEqual((expected_masterip, expected_vm_dict), (returned_masterip, returned_vm_dict))

    # more testcases go here

    # free up any resources not automatically released
    def tearDown(self):
        pass


if __name__ == '__main__':
    main()
