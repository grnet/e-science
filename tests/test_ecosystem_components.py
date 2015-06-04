#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import logging
from os.path import join, dirname, abspath
import subprocess
from ConfigParser import RawConfigParser, NoSectionError
from orka.orka.utils import get_user_clusters, ssh_call_hadoop, ssh_check_output_hadoop, ssh_stream_to_hadoop
import unittest
from __builtin__ import file
sys.path.append(dirname(abspath(__file__)))
from constants_of_tests import *
from orka.orka.cluster_errors_constants import error_fatal, const_hadoop_status_started, FNULL
import requests
import re

BASE_DIR = join(dirname(abspath(__file__)), "../")
JOB_PROPERTIES_PATH = join(dirname(abspath(__file__)), 'job.properties')

class EcosystemTest(unittest.TestCase):
    """
    A Test suite for testing Ecosystem components
    """
    def setUp(self):
        """
        Set up the arguments that every test will use.
        """
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        self.name = 'ecosystemtest'
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
                        self.wordcount_command = WORDCOUNT
                        self.hadoop_path = HADOOP_PATH
                        self.user = 'hduser'
                        self.VALID_DEST_DIR = '/user/hduser'
                        self.hdfs_path = HDFS_PATH
                        self.oozie_command = OOZIE_ECOSYSTEM_COMMAND.format(self.master_IP)
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
                  
                  
    def test_pig(self):
        """
        Test pig for hadoop ecosystem
        """
        pig_command = "export JAVA_HOME=/usr/lib/jvm/java-8-oracle; export HADOOP_HOME=/usr/local/hadoop; /usr/local/pig/bin/pig -e \"fs -mkdir /tmp/pig_test_folder\""
        ssh_call_hadoop(self.user, self.master_IP, pig_command, hadoop_path='')
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e /tmp/{0}'.format('pig_test_folder'))
        self.assertEqual(exist_check_status, 0)
        self.addCleanup(self.delete_hdfs_files, '/tmp/pig_test_folder', prefix="-r")
        
    def test_spark_pi_wordcount(self):
        """
        Functional test to check if Spark is working correctly in a Ecosystem cluster
        by running a Spark Pi and a Spark WordCount.
        """
        self.put_file_to_hdfs('/tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))
        spark_job = 'export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop; /usr/local/spark/bin/spark-submit --class org.apache.spark.examples.'

        for job_properties in [('SparkPi', 10), ('JavaWordCount', SOURCE_HDFS_TO_PITHOS_FILE)]:
            test_job = spark_job + '{0} --deploy-mode cluster --master yarn-cluster {1} {2}'.format(job_properties[0], SPARK_ECOSYSTEM_EXAMPLES, job_properties[1])
            exist_check_status = ssh_call_hadoop(self.user, self.master_IP, test_job, hadoop_path='')
            self.assertEqual(exist_check_status, 0)

        self.addCleanup(self.delete_hdfs_files, SOURCE_HDFS_TO_PITHOS_FILE)
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/{0}'.format(SOURCE_HDFS_TO_PITHOS_FILE))

    def test_compare_mapreduce_wordcount_pithos_hdfs(self):
        """
        Functional test to upload a test file in Pithos and run two MapReduce wordcounts
        in a Ecosystem cluster, one from Pithos and one native from HDFS and compare the
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
    
    def test_hive_count_rows_in_table_exists(self):
        """
        Functional test for Ecosystem Hive
        creates a table (if not exists)
        and counts rows in this table 
        """
        # create a table
        hive_command = "hive -e 'CREATE TABLE IF NOT EXISTS hive_table ( age int, name String );'"
        ssh_call_hadoop(self.user, self.master_IP, hive_command, hadoop_path='/usr/local/hive/bin/')
        
        # count rows
        hive_command_count = "hive -e 'select count(*) from hive_table';"
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP, hive_command_count, hadoop_path='/usr/local/hive/bin/')
        
        self.assertEqual(exist_check_status, 0) # OK
        
        # Remove test table
        hive_command = "hive -e 'DROP TABLE hive_table;'"
        ssh_call_hadoop(self.user, self.master_IP, hive_command, hadoop_path='/usr/local/hive/bin/')

    def test_hive_count_rows_in_table_not_exist(self):
        """
        Functional test for Ecosystem Hive
        count rows in a table that does not exist 
        """
        hive_command = "hive -e 'select count(*) from table_not_exist';"
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP, hive_command, hadoop_path='/usr/local/hive/bin/')
        
        self.assertEqual(exist_check_status, 17) # ERROR table not found
        
    def test_hbase_table_not_exist(self):
        """
        Functional test for Ecosystem HBase
        check if a table does not exist
        """
        baseurl = "http://" + self.master_IP + ":16010"
        # check for a table that does not exist
        request = requests.get(baseurl + "/table.jsp?name=" + "table_not_exist")
        self.assertEqual(request.status_code, 500) # NOT FOUND HBASE EXCEPTION
        
    def test_hbase_table_exists(self):
        """
        Functional test for Ecosystem HBase
        create a table and then
        check if the table exists
        """
        baseurl = "http://" + self.master_IP + ":16010"                
        tablename = "testtable"
              
        # Create shell script so as to create the table
        self.hadoop_local_fs_action("echo " + "create \\'testtable\\', \\'cf\\'" + " > {0} && echo exit >> {0}".format(HBASE_SCRIPT_PATH))
        hbase_command = "hbase shell " + HBASE_SCRIPT_PATH
        ssh_call_hadoop(self.user, self.master_IP, hbase_command, hadoop_path='/usr/local/hbase/bin/')
        
        # Check if table exists
        request = requests.get(baseurl + "/table.jsp?name=" + tablename)   
        self.assertEqual(request.status_code, 200) # OK
        
        # Remove test data
        self.hadoop_local_fs_action("echo disable \\'testtable\\' > {0} && echo drop \\'testtable\\' >> {0} && echo exit >> {0}".format(HBASE_SCRIPT_PATH))
        ssh_call_hadoop(self.user, self.master_IP, hbase_command, hadoop_path='/usr/local/hbase/bin/')
        self.addCleanup(self.hadoop_local_fs_action, 'rm ' + HBASE_SCRIPT_PATH)
        
    def test_oozie_status_normal(self):
        """
        Functional test for Ecosystem Oozie
        checks if status is normal
        """
        # ensure that oozie is running
        response = subprocess.call( "ssh " + "root" + "@" + self.master_IP + " \"" + 
                                    "service oozieserver restart" + "\""
                                    , stderr=FNULL, shell=True)                
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "/usr/local/oozie/bin/oozie admin -status -oozie http://" + self.master_IP + ":11000/oozie" + "\""
                                    , stderr=FNULL, shell=True)        
        self.assertEqual(response, 0) # NORMAL

    def test_oozie_status_down(self):
        """
        Functional test for Ecosystem Oozie
        checks if oozie is down
        """
        # stop oozie
        response = subprocess.call( "ssh " + "root" + "@" + self.master_IP + " \"" + 
                                    "service oozieserver stop" + "\""
                                    , stderr=FNULL, shell=True)                
        response = subprocess.call( "ssh " + self.user + "@" + self.master_IP + " \"" + 
                                    "/usr/local/oozie/bin/oozie admin -status -oozie http://" + self.master_IP + ":11000/oozie" + "\""
                                    , stderr=FNULL, shell=True)        
        self.assertEqual(response, 255) # Oozie down
        
    def test_oozie(self):
        """
        Test oozie for Ecosystem cluster
        """
        master_vm_hostname = ssh_check_output_hadoop(self.user, self.master_IP, 'cat /etc/hostname', hadoop_path='')[0]
        read_workflow = open("workflow_ecosystem.xml", "r").read()
        workflow_file = open("workflow_ecosystem.xml", "w")
        workflow_file.write( re.sub("hostname", master_vm_hostname, read_workflow) )
        workflow_file.close()
        ssh_call_hadoop(self.user, self.master_IP, 'dfs -mkdir oozie_app', hadoop_path=self.hdfs_path)
        ssh_stream_to_hadoop(self.user, self.master_IP, join(dirname(abspath(__file__)), "workflow_ecosystem.xml"),
                             self.VALID_DEST_DIR + "/oozie_app/workflow.xml", hadoop_path=self.hdfs_path)
        job_properties = JOB_PROPERTIES_ECOSYSTEM_TEMPLATE.format(master_vm_hostname)

        create_job_properties_file = 'echo -e "{0}" > job.properties'.format(job_properties)
        subprocess.call(create_job_properties_file, stderr=FNULL, shell=True)
        subprocess.call( "scp {0} {1}@{2}:/tmp/".format(JOB_PROPERTIES_PATH, self.user, self.master_IP),
                         stderr=FNULL, shell=True)
        ssh_call_hadoop(self.user, self.master_IP, self.oozie_command, hadoop_path='')
        exist_check_status = ssh_call_hadoop(self.user, self.master_IP,
                                             ' dfs -test -e {0}/{1}'.format(OOZIE_TEST_FOLDER, "oozie_test_folder"),
                                             hadoop_path=self.hdfs_path)
        self.assertEqual(exist_check_status, 0)
        self.addCleanup(self.delete_hdfs_files, OOZIE_TEST_FOLDER, prefix="-r")
        self.addCleanup(self.hadoop_local_fs_action, 'rm /tmp/job.properties')
        self.addCleanup(self.delete_local_files, JOB_PROPERTIES_PATH)
        workflow_file = open("workflow_ecosystem.xml", "w")
        workflow_file.write( re.sub(master_vm_hostname, "hostname", read_workflow) )
        workflow_file.close()
    
    def put_file_to_hdfs(self, file_to_create):
        """
        Helper method to create file in Hdfs before test.
        """
        self.hadoop_local_fs_action('echo "test file for hdfs" > {0}'.format(file_to_create))
        ssh_call_hadoop(self.user, self.master_IP, ' dfs -put {0}'.format(file_to_create),
                        hadoop_path=self.hdfs_path)    
    
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


    def hadoop_local_fs_action(self, action):
        """
        Helper method to perform action given on local filesystem of a master VM.
        """
        subprocess.call("ssh {0}@".format(self.user) + self.master_IP + " \"" + action +
                        "\"", stderr=FNULL, shell=True)
        
    def delete_pithos_files(self, file_to_delete):
        """
        Helper method to delete files transfered to pithos filesystem after test.
        """
        subprocess.call('kamaki file delete --yes {}'.format(file_to_delete), stderr=FNULL, shell=True)

    def tearDown(self):
        """
        tearDown method for unit test class.
        """
        print 'Cleaning up temp files'


if __name__ == '__main__':
    unittest.main()
