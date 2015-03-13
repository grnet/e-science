#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from ConfigParser import RawConfigParser, NoSectionError
from os.path import join, dirname, abspath
from orka.orka.utils import get_user_clusters
from orka.orka.orka import HadoopCluster
import unittest, time, re
from orka.orka.cluster_errors_constants import error_fatal, const_hadoop_status_started
SOURCE_ERROR_FILE = 'file_that_does_not_exist_hopefully'
SOURCE_FILE = 'README.md'
DEST_FILE = 'destination_hdfs_file_non_existant'
DEST_DIR = '/user/hduser'
DEST_ERROR_DIR = 'a_directory_that_by_all_means_should_not_exist'

BASE_DIR = join(dirname(abspath(__file__)), "../")

class OrkaTest(unittest.TestCase):
    """
    Class
    """
    def setUp(self):
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
            clusters = get_user_clusters(self.token)
            self.active_cluster = None
            for cluster in clusters:
                if (cluster['master_IP'] == self.master_IP):
                    if cluster['hadoop_status'] == const_hadoop_status_started:
                        self.active_cluster = cluster
                        break
            else:
                logging.error(' You can take file actions on active clusters with started hadoop only.')
                exit(error_fatal)
            self.opts = {'source':'','destination':'', 'token':self.token, 'cluster_id': self.active_cluster['id'],
                         'auth_url':self.auth_url}
            # auth = check_credentials(self.token)
            # try:
            #     list_of_projects = auth.get_projects(state='active')
            # except Exception:
            #     self.assertTrue(False,'Could not get list of projects')
            # for project in list_of_projects:
            #     if project['name'] == self.project_name:
            #         self.project_id = project['id']
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            self.project_name = "INVALID_PROJECT_NAME"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    def test_error_source_file(self):

        self.opts.update({'source': SOURCE_ERROR_FILE})
        t_hadoopcluster = HadoopCluster(self.opts)
        # status=t_hadoopcluster.put_from_local(self.active_cluster)
        #self.assertEqual(status, error_fatal)
        self.assertRaises(IOError, t_hadoopcluster.put_from_local, self.active_cluster)
        # SystemExit instead of IOError

    def test_check_hdfs_path(self):

        self.opts.update({'destination': DEST_FILE })
        t_hadoopcluster = HadoopCluster(self.opts)
        status = t_hadoopcluster.check_hdfs_path(self.master_IP, self.opts['destination'], '-e')
        self.assertNotEqual(status, 0)

        self.opts.update({'destination': DEST_DIR })
        t_hadoopcluster = HadoopCluster(self.opts)
        status = t_hadoopcluster.check_hdfs_path(self.master_IP, self.opts['destination'], '-d')
        self.assertEqual(status, 0)

        self.opts.update({'destination': DEST_ERROR_DIR })
        t_hadoopcluster = HadoopCluster(self.opts)
        self.assertRaises(SystemExit, t_hadoopcluster.check_hdfs_path, self.master_IP, self.opts['destination'], '-d')




if __name__ == '__main__':
    unittest.main()