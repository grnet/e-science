#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os, sys
from os.path import join, dirname, abspath
sys.path.append(dirname(abspath(__file__)))
from constants_of_tests import *
import subprocess
from ConfigParser import RawConfigParser, NoSectionError
from orka.orka.utils import get_user_clusters, ssh_call_hadoop, ssh_check_output_hadoop
from orka.orka.orka import HadoopCluster
import unittest
from mock import patch
from orka.orka.cluster_errors_constants import error_fatal, const_hadoop_status_started, FNULL

BASE_DIR = join(dirname(abspath(__file__)), "../")


# mock function for file size checking test.
def mock_get_dfs_remaining(*args):
    """
    mock ssh_check_output_hadoop for dfsadmin report, returning dfs remaining
    """
    return ['Configured Capacity: 9001 (over 9000 GB)', 'DFS Remaining: 0 (0 GB)']


class OrkaTest(unittest.TestCase):
    """
    A Test suite for orka-cli put/get command.
    """
    def setUp(self):
        """
        Set up the arguments that every unit test for put/get will use.
        """
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        self.name = 'orkatest'
        parser.read(config_file)
        try:
            self.token = parser.get('cloud \"~okeanos\"', 'token')
            self.auth_url = parser.get('cloud \"~okeanos\"', 'url')
            self.base_url = parser.get('deploy', 'url')
            self.project_name = parser.get('project', 'name')
            self.master_IP = parser.get('cluster', 'master_ip')
            clusters = get_user_clusters(self.token, self.base_url)
            self.active_cluster = None
            for cluster in clusters:
                if cluster['master_IP'] == self.master_IP:
                    if cluster['hadoop_status'] == const_hadoop_status_started:
                        self.active_cluster = cluster
                        self.wordcount_command = WORDCOUNT
                        self.hadoop_path = HADOOP_PATH
                        self.user = 'hduser'
                        self.hdfs_path = HDFS_PATH
                        self.VALID_DEST_DIR = '/user/{0}'.format(self.user)
                        if 'cdh' in self.active_cluster['os_image']:
                            self.wordcount_command = CLOUDERA_WORDCOUNT
                            self.hadoop_path = CLOUDERA_HADOOP_PATH
                            self.user = 'root'
                            self.VALID_DEST_DIR = '/user/hdfs'
                            self.hdfs_path = CLOUDERA_HDFS_PATH
                        break
            else:
                logging.error(' You can take file actions on active clusters with started hadoop only.')
                exit(error_fatal)
            self.opts = {'source': '', 'destination': '', 'token': self.token, 'cluster_id': self.active_cluster['id'],
                         'auth_url': self.auth_url, 'user': '', 'password': '', 'server_url': self.base_url}
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            self.project_name = "INVALID_PROJECT_NAME"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    def test_error_source_file(self):
        """
        unit testing if correct exception is raised when input file is invalid.
        """
        self.opts.update({'source': INVALID_SOURCE_FILE})
        t_hadoopcluster = HadoopCluster(self.opts)
        self.assertRaises(IOError, t_hadoopcluster.put_from_local, self.active_cluster)

    def test_check_hdfs_path_dest_file(self):
        """
        unit testing that check_hdfs_path method returns correct value when file does not exist in hdfs.
        """
        self.opts.update({'destination': VALID_DEST_FILE})
        t_hadoopcluster = HadoopCluster(self.opts)
        status = t_hadoopcluster.check_hdfs_path(self.master_IP, self.opts['destination'], '-e')
        self.assertNotEqual(status, 0)

    def test_check_hdfs_path_dest_dir(self):
        """
        unit testing that check_hdfs_path method returns correct value when directory does exist in hdfs.
        """
        self.opts.update({'destination': self.VALID_DEST_DIR})
        t_hadoopcluster = HadoopCluster(self.opts)
        status = t_hadoopcluster.check_hdfs_path(self.master_IP, self.opts['destination'], '-d')
        self.assertEqual(status, 0)

    def test_check_hdfs_path_dest_error_dir(self):
        """
        unit testing that check_hdfs_path method raises correct exception when directory does exist in hdfs.
        """
        self.opts.update({'destination': INVALID_DEST_DIR})
        t_hadoopcluster = HadoopCluster(self.opts)
        self.assertRaises(SystemExit, t_hadoopcluster.check_hdfs_path, self.master_IP, self.opts['destination'], '-d')

    def test_put_from_local(self):
        """
        functional test to put file from local to hdfs and check that file now exists in hdfs and is not zero size.
        """
        subprocess.call('echo "this is a unit test file for local to hdfs orka-cli put." > {0}'.format(SOURCE_LOCAL_TO_HDFS_FILE),
                        stderr=FNULL, shell=True)
        self.opts.update({'source': SOURCE_LOCAL_TO_HDFS_FILE, 'destination': [DEST_LOCAL_TO_HDFS_FILE],
                         'fileput': True})
        HadoopCluster(self.opts).file_action()
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e {0}'.format(DEST_LOCAL_TO_HDFS_FILE),
                                             hadoop_path=self.hdfs_path)
        zero_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                            ' dfs -test -z {0}'.format(DEST_LOCAL_TO_HDFS_FILE),
                                            hadoop_path=self.hdfs_path)
        self.assertEqual(exist_check_status, 0) and self.assertEqual(zero_check_status, 1)
        self.addCleanup(self.delete_hdfs_files, DEST_LOCAL_TO_HDFS_FILE)
        self.addCleanup(self.delete_local_files, self.opts['source'])

    def test_put_from_local_recursive(self):
        """
        functional test to put files inside a folder from local to hdfs and check all the files now exist in hdfs and is not zero size.
        """
        list_of_files = []
        for i in range(10):
            subprocess.call('echo "this is the unit test file {0} for local to hdfs orka-cli put." > {0}{1}'.format(i, SOURCE_LOCAL_TO_HDFS_FILE),
                            stderr=FNULL, shell=True)
            list_of_files.append('{0}{1}'.format(i, SOURCE_LOCAL_TO_HDFS_FILE))
        list_of_files.append('/user/hduser')
        list_of_files.remove('0{0}'.format(SOURCE_LOCAL_TO_HDFS_FILE))
        self.opts.update({'source': '0{0}'.format(SOURCE_LOCAL_TO_HDFS_FILE), 'destination': list_of_files,
                         'fileput': True})
        HadoopCluster(self.opts).file_action()
        list_of_files.insert(0, '0{0}'.format(SOURCE_LOCAL_TO_HDFS_FILE))
        for file in list_of_files[:-1]:
            exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                                 ' dfs -test -e {0}'.format(file),
                                                 hadoop_path=self.hdfs_path)
            zero_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                                ' dfs -test -z {0}'.format(file),
                                                hadoop_path=self.hdfs_path)
            self.assertEqual(exist_check_status, 0) and self.assertEqual(zero_check_status, 1)
            self.addCleanup(self.delete_hdfs_files, '/user/hduser/{0}'.format(file))
            self.addCleanup(self.delete_local_files, file)

    def test_get_from_hdfs_to_pithos(self):
        """
        functional test to get a test file from hdfs to pithos and check that file exists.
        """
        self.put_file_to_hdfs('/tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))
        self.opts.update({'source': SOURCE_HDFS_TO_PITHOS_FILE, 'destination': DEST_HDFS_TO_PITHOS_FILE})
        HadoopCluster(self.opts).get_from_hadoop_to_pithos(self.active_cluster, self.opts['destination'])
        exist_check_status = os.system('kamaki file list | grep {0}'.format(self.opts['destination']))
        self.assertEqual(exist_check_status, 0)
        self.addCleanup(self.delete_pithos_files, self.opts['destination'])
        self.addCleanup(self.delete_hdfs_files, self.opts['source'])
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))

    def test_put_from_remote(self):
        """
        functional test to put file from remote server to Hdfs and check that file now exists in Hdfs and
        is not zero size.
        """
        self.opts.update({'source': SOURCE_REMOTE_TO_HDFS_FILE, 'destination': DEST_REMOTE_TO_HDFS_FILE, 'user': '',
                          'password': ''})
        HadoopCluster(self.opts).put_from_server()
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e {0}'.format(self.opts['destination']),
                                             hadoop_path=self.hdfs_path)
        zero_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                            ' dfs -test -z {0}'.format(self.opts['destination']),
                                            hadoop_path=self.hdfs_path)
        self.assertEqual(exist_check_status, 0) and self.assertEqual(zero_check_status, 1)
        self.addCleanup(self.delete_hdfs_files, self.opts['destination'])

    def test_put_from_pithos(self):
        """
        functional test to put file from Pithos to Hdfs and check that file now exists in Hdfs and
        is not zero size.
        """
        subprocess.call('echo "this is a test file for pithos to hdfs orka-cli put" > {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE),
                        stderr=FNULL, shell=True)
        subprocess.call('kamaki file upload {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE), stderr=FNULL, shell=True)
        self.opts.update({'destination': DEST_PITHOS_TO_HDFS_FILE})
        HadoopCluster(self.opts).put_from_pithos(self.active_cluster, SOURCE_PITHOS_TO_HDFS_FILE)
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e {0}'.format(self.opts['destination']),
                                             hadoop_path=self.hdfs_path)
        zero_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                            ' dfs -test -z {0}'.format(self.opts['destination']),
                                            hadoop_path=self.hdfs_path)
        self.assertEqual(exist_check_status, 0) and self.assertEqual(zero_check_status, 1)
        self.addCleanup(self.delete_hdfs_files, self.opts['destination'])
        self.addCleanup(self.delete_pithos_files, SOURCE_PITHOS_TO_HDFS_FILE)
        self.addCleanup(self.delete_local_files, SOURCE_PITHOS_TO_HDFS_FILE)

    def test_get_from_hdfs_to_local(self):
        """
        functional test to get file from Hdfs and check that file now exists in local filesystem.
        """
        self.put_file_to_hdfs('/tmp/{0}'.format(SOURCE_HDFS_TO_LOCAL_FILE))
        self.opts.update({'source': SOURCE_HDFS_TO_LOCAL_FILE, 'destination': DEST_HDFS_TO_LOCAL_FILE})
        HadoopCluster(self.opts).get_from_hadoop_to_local(self.active_cluster)
        exist_check_status = os.system('ls {0}'.format(self.opts['destination']))
        self.assertEqual(exist_check_status, 0)
        self.addCleanup(self.delete_hdfs_files, self.opts['source'])
        self.addCleanup(self.delete_local_files, self.opts['destination'])
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/{0}'.format(SOURCE_HDFS_TO_LOCAL_FILE))

    def test_run_wordcount_from_pithos(self):
        """
        Functional test to upload a test file in Pithos and run a wordcount streaming the file from Pithos.
        """
        subprocess.call('echo "this is a test file to run a streaming wordcount" > {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE),
                        stderr=FNULL, shell=True)
        subprocess.call('kamaki file upload {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE), stderr=FNULL, shell=True)
        ssh_call_hadoop(self.user, self.master_IP, self.wordcount_command + 'pithos://pithos/{0} {1}'.
                        format(SOURCE_PITHOS_TO_HDFS_FILE, PITHOS_WORDCOUNT_DIR),
                                             hadoop_path=self.hadoop_path)

        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e {0}/_SUCCESS'.format(PITHOS_WORDCOUNT_DIR),
                                             hadoop_path=self.hdfs_path)
        self.assertEqual(exist_check_status, 0)
        self.addCleanup(self.delete_hdfs_files, PITHOS_WORDCOUNT_DIR, prefix="-r")
        self.addCleanup(self.delete_local_files, SOURCE_PITHOS_TO_HDFS_FILE)
        self.addCleanup(self.delete_pithos_files, SOURCE_PITHOS_TO_HDFS_FILE)

    def test_compare_wordcount_pithos_hdfs(self):
        """
        Functional test to upload a test file in Pithos and run two wordcounts, one from Pithos and one native from HDFS
        and compare the length of the output files.
        """
        subprocess.call('echo "this is a test file to run a wordcount" > {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE),
                        stderr=FNULL, shell=True)
        subprocess.call('kamaki file upload {0}'.format(SOURCE_PITHOS_TO_HDFS_FILE), stderr=FNULL, shell=True)

        ssh_call_hadoop(self.user, self.master_IP, 'kamaki file download {0} /tmp/{0}'.
                        format(SOURCE_PITHOS_TO_HDFS_FILE), hadoop_path='')
        ssh_call_hadoop(self.user, self.master_IP, ' dfs -put /tmp/{0}'.
                        format(SOURCE_PITHOS_TO_HDFS_FILE),hadoop_path=self.hdfs_path)

        ssh_call_hadoop(self.user, self.master_IP, self.wordcount_command + 'pithos://pithos/{0} {1}'.
                        format(SOURCE_PITHOS_TO_HDFS_FILE, PITHOS_WORDCOUNT_DIR),
                                             hadoop_path=self.hadoop_path)
        ssh_call_hadoop(self.user, self.master_IP, self.wordcount_command + '{0} {1}'.
                        format(SOURCE_PITHOS_TO_HDFS_FILE, HDFS_WORDCOUNT_DIR),
                                             hadoop_path=self.hadoop_path)

        bytes_pithos_written = ssh_check_output_hadoop(self.user, self.master_IP,
                                             ' dfs -dus {0}'.format(PITHOS_WORDCOUNT_DIR),
                                             hadoop_path=self.hdfs_path)
        bytes_hdfs_written = ssh_check_output_hadoop(self.user, self.master_IP,
                                             ' dfs -dus {0}'.format(HDFS_WORDCOUNT_DIR),
                                             hadoop_path=self.hdfs_path)

        self.assertEqual(bytes_pithos_written[0].replace(PITHOS_WORDCOUNT_DIR, ""),
                         bytes_hdfs_written[0].replace(HDFS_WORDCOUNT_DIR, ""))
        self.addCleanup(self.delete_hdfs_files, PITHOS_WORDCOUNT_DIR, prefix="-r")
        self.addCleanup(self.delete_hdfs_files, HDFS_WORDCOUNT_DIR, prefix="-r")
        self.addCleanup(self.delete_hdfs_files, SOURCE_PITHOS_TO_HDFS_FILE)
        self.addCleanup(self.delete_local_files, SOURCE_PITHOS_TO_HDFS_FILE)
        self.addCleanup(self.delete_pithos_files, SOURCE_PITHOS_TO_HDFS_FILE)
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/{0}'.format(SOURCE_PITHOS_TO_HDFS_FILE))


    def delete_hdfs_files(self, file_to_delete, prefix=""):
        """
        Helper method to delete files transfered to hdfs filesystem after test.
        """
        ssh_call_hadoop(self.user, self.master_IP, ' dfs -rm {0} {1}'.format(prefix, file_to_delete),
                        hadoop_path=self.hdfs_path)

    def delete_local_files(self, file_to_delete):
        """
        Helper method to delete files transfered to local filesystem after test.
        """
        if os.path.isfile(file_to_delete):
            os.remove(file_to_delete)
        else:
            print("Error: {0} test file not found".format(file_to_delete))

    def delete_pithos_files(self, file_to_delete):
        """
        Helper method to delete files transfered to pithos filesystem after test.
        """
        subprocess.call('kamaki file delete --yes {}'.format(file_to_delete), stderr=FNULL, shell=True)

    def put_file_to_hdfs(self, file_to_create):
        """
        Helper method to create file in Hdfs before test.
        """
        self.hadoop_local_fs_action('echo "test file for hdfs" > {0}'.format(file_to_create))
        ssh_call_hadoop(self.user, self.master_IP, ' dfs -put {0}'.format(file_to_create),
                        hadoop_path=self.hdfs_path)

    def hadoop_local_fs_action(self, action):
        """
        Helper method to perform action given on local filesystem of a master VM.
        """
        subprocess.call("ssh {0}@".format(self.user) + self.master_IP + " \"" + action +
                        "\"", stderr=FNULL, shell=True)

    def tearDown(self):
        """
        tearDown method for unit test class.
        """
        print 'Cleaning up temp files'

    @patch('orka.orka.orka.ssh_check_output_hadoop', mock_get_dfs_remaining)
    def test_file_size_put_from_local(self):
        """
        Testing, using mock, if the put from Local to Hdfs method raises correct exception when file is bigger than
        available space.
        """
        subprocess.call('echo "this is a unit test file for local to hdfs orka-cli put." > {0}'.format(SOURCE_LOCAL_TO_HDFS_FILE),
                        stderr=FNULL, shell=True)
        self.opts.update({'source': SOURCE_LOCAL_TO_HDFS_FILE, 'destination': DEST_LOCAL_TO_HDFS_FILE})
        t_hadoopcluster = HadoopCluster(self.opts)
        self.assertRaises(SystemExit, t_hadoopcluster.put_from_local, self.active_cluster)
        self.addCleanup(self.delete_local_files, self.opts['source'])

if __name__ == '__main__':
    unittest.main()