#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import logging
from os.path import join, dirname, abspath
import subprocess
from ConfigParser import RawConfigParser, NoSectionError
from orka.orka.utils import get_user_clusters, ssh_call_hadoop, ssh_check_output_hadoop
import unittest
sys.path.append(dirname(abspath(__file__)))
from constants_of_tests import *
from orka.orka.cluster_errors_constants import error_fatal, const_hadoop_status_started, FNULL
import requests

BASE_DIR = join(dirname(abspath(__file__)), "../")


class ClouderaTest(unittest.TestCase):
    """
    A Test suite for testing Cloudera components
    """
    def setUp(self):
        """
        Set up the arguments that every test will use.
        """
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        self.name = 'clouderatest'
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
                if cluster['master_IP'] == self.master_IP:
                    if cluster['hadoop_status'] == const_hadoop_status_started:
                        self.active_cluster = cluster
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
                         'auth_url': self.auth_url, 'user': '', 'password': ''}
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            self.project_name = "INVALID_PROJECT_NAME"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    def test_oozie_status_normal(self):
        """
        Functional test for Cloudera Oozie
        checks if status is normal
        """
        # ensure that oozie is running
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "service oozie restart" + "\""
                                    , stderr=FNULL, shell=True)                
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "oozie admin -status -oozie http://" + self.master_IP + ":11000/oozie" + "\""
                                    , stderr=FNULL, shell=True)        
        self.assertEqual(response, 0) # NORMAL

    def test_oozie_status_down(self):
        """
        Functional test for Cloudera Oozie
        checks if oozie is down
        """
        # stop oozie
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "service oozie stop" + "\""
                                    , stderr=FNULL, shell=True)                
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "oozie admin -status -oozie http://" + self.master_IP + ":11000/oozie" + "\""
                                    , stderr=FNULL, shell=True)        
        self.assertEqual(response, 255) # Oozie down
        
    def test_hive_count_rows_in_table_exists(self):
        """
        Functional test for Cloudera Hive
        creates a table (if not exists)
        and counts rows in this table 
        """
        # create a table
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "hive -e 'CREATE TABLE IF NOT EXISTS hive_table ( age int, name String );'" + "\""
                                    , stderr=FNULL, shell=True)
        # count rows
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "hive -e 'select count(*) from hive_table';" + "\""
                                    , stderr=FNULL, shell=True)
        self.assertEqual(response, 0) # OK

    def test_hive_count_rows_in_table_not_exists(self):
        """
        Functional test for Cloudera Hive
        count rows in a table that does not exist 
        """
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "hive -e 'select count(*) from table_not_exists';" + "\""
                                    , stderr=FNULL, shell=True)
        self.assertEqual(response, 17) # ERROR table not found

    def test_hbase_table_not_exists(self):
        """
        Functional test for Cloudera HBase
        check if a table does not exist
        """
        baseurl = "http://" + self.master_IP + ":60050"
        # check for a table that does not exist
        request = requests.get(baseurl + "/" + "table_not_exists" + "/schema")
        self.assertEqual(request.status_code, 404) # NOT FOUND

    def test_hbase_table_exists(self):
        """
        Functional test for Cloudera HBase
        create a table and then
        check if the table exists
        """
        baseurl = "http://" + self.master_IP + ":60050"                
        tablename = "testtable"
        cfname = "testcolumn1"
        # delete it first (if already exists)
        request = requests.delete(baseurl + "/" + tablename + "/schema")        
        # Create XML for table
        content =  '<?xml version="1.0" encoding="UTF-8"?>'
        content += '<TableSchema name="' + tablename + '">'
        content += '  <ColumnSchema name="' + cfname + '" />'
        content += '</TableSchema>'
        # Create the table
        request = requests.post(baseurl + "/" + tablename + "/schema", 
                                data=content, headers={"Content-Type" : "text/xml", "Accept" : "text/xml"})       
        self.assertEqual(request.status_code, 201) # CREATED
        # Check if table exists
        request = requests.get(baseurl + "/" + tablename + "/schema")   
        self.assertEqual(request.status_code, 200) # OK

    def test_spark_pi_wordcount(self):
        """
        Functional test to check if Spark is working correctly in a Cloudera cluster
        by running a Spark Pi and a Spark WordCount.
        """
        self.put_file_to_hdfs('/tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))
        spark_job = 'sudo -u hdfs spark-submit --class org.apache.spark.examples.'

        for job_properties in [('SparkPi', 10), ('JavaWordCount', SOURCE_HDFS_TO_PITHOS_FILE)]:
            test_job = spark_job + '{0} --deploy-mode cluster --master yarn-cluster {1} {2}'.format(job_properties[0], SPARK_EXAMPLES, job_properties[1])
            ssh_call_hadoop(self.user, self.master_IP, test_job, hadoop_path='')

        self.addCleanup(self.delete_hdfs_files, SOURCE_HDFS_TO_PITHOS_FILE)
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))

    def test_compare_mapreduce_wordcount_pithos_hdfs(self):
        """
        Functional test to upload a test file in Pithos and run two MapReduce wordcounts
        in a Cloudera cluster, one from Pithos and one native from HDFS and compare the
        length of the output files.
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


if __name__ == '__main__':
    unittest.main()
