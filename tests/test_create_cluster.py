# setup testing framework
from unittest import TestCase,main
from mock import patch

# get relative path references so imports will work,
# even if __init__.py is missing (/tests is a simple directory not a module)
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import objects we aim to test
from create_bare_cluster import create_cluster

# mock unmanaged resources
def mock_createcluster(*args):
    print 'in mock create cluster'
    fakeip = '127.0.0.1'
    fakevmdict = {1: 'f vm'}
    return fakeip, fakevmdict

def mock_sleep(*args):
    print 'in mock sleep'

def mock_checkcredentials(*args):
    print 'in mock check credentials'

def mock_endpoints_userid(arg1):
    print 'in mock endpoints'
    fakeuid = 'id'
    fakeendpoints = {'cyclades': 0, 'plankton': 0, 'network': 0}
    return fakeendpoints, fakeuid

def mock_init_cyclades(*args):
    print 'in mock cyclades'

def mock_get_flavorid(*args):
    print 'in mock flavor id'
    return 1

def mock_check_quota(*args):
    print 'in mock check quota'

class mock_plankton():
    def list_public(self,*args):
        return [{'name':'','id':0}]

def mock_init_plankton(*args):
    print 'in mock init plankton'
    plist = mock_plankton()
    return plist

def mock_init_cyclades_netclient(*args):
    print 'in mock init cyclades netclient'

# replace unmanaged calls with the mocks
@patch('create_bare_cluster.Cluster.create', mock_createcluster)
@patch('create_bare_cluster.check_credentials', mock_checkcredentials)
@patch('create_bare_cluster.endpoints_and_user_id', mock_endpoints_userid)
@patch('create_bare_cluster.init_cyclades', mock_init_cyclades)
@patch('create_bare_cluster.get_flavor_id', mock_get_flavorid)
@patch('create_bare_cluster.check_quota', mock_check_quota)
@patch('create_bare_cluster.init_plankton', mock_init_plankton)
@patch('create_bare_cluster.init_cyclades_netclient', mock_init_cyclades_netclient)
@patch('create_bare_cluster.sleep', mock_sleep)
class TestCreateCluster(TestCase):
    # initialize objects common to all tests in this test case
    def setUp(self):
        pass

    def test_create_cluster(self):
        # arrange
        fakeip = '127.0.0.1'
        fakevmdict = {1: 'f vm'}
        # act
        retip, retvmdict = create_cluster('',0,0,0,0,'',0,0,0,'','')
        # assert
        self.assertEqual((fakeip,fakevmdict),(retip,retvmdict))

    # more tests go here

    # free up any resources not automatically released
    def tearDown(self):
        pass

if __name__ == '__main__':
    main()