# setup testing framework
from unittest import TestCase,main
from nose.tools import assert_equal,assert_raises
from mock import Mock,patch

# get relative path references so imports will work,
# even if __init__.py is missing (/tests is a simple directory not a module)
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import objects we aim to test
from create_bare_cluster import create_cluster
from okeanos_utils import Cluster


class TestCreate_cluster(TestCase):
    # initialize objects common to all tests in this test case
    def setUp(self):
        self.mock_cluster = Mock(Cluster)

    def test_create_cluster(self):
        # arrange
        self.mock_cluster.create.return_value = "127.0.0.1"
        # act
        cluster = self.mock_cluster.create()
        # assert
        self.assertEqual(cluster,"127.0.0.1")

    # free up any resources not automatically released
    def tearDown(self):
        pass

if __name__ == '__main__':
    main()