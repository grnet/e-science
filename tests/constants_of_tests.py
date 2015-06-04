#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File names for the unit tests
INVALID_SOURCE_FILE = 'file_that_does_not_exist_hopefully'
VALID_DEST_FILE = 'destination_hdfs_file_non_existant'
INVALID_DEST_DIR = 'a_directory_that_by_all_means_should_not_exist'

# Source and destination file names for functional tests
# Put Local to Hdfs
SOURCE_LOCAL_TO_HDFS_FILE = 'test_file_local_to_hdfs.txt'
DEST_LOCAL_TO_HDFS_FILE = 'test_file_hdfs_from_local.txt'

# Get from Hdfs to Local
SOURCE_HDFS_TO_LOCAL_FILE = 'test_file_hdfs_to_local.txt'
DEST_HDFS_TO_LOCAL_FILE = 'test_file_local_from_hdfs.txt'

# Put from Ftp/Http server to Hdfs
SOURCE_REMOTE_TO_HDFS_FILE = 'https://dumps.wikimedia.org/elwiki/latest/elwiki-latest-pages-meta-current.xml.bz2'
DEST_REMOTE_TO_HDFS_FILE = 'elwiki-latest-pages-meta-current.xml.bz2'

# Put from Pithos to Hdfs
SOURCE_PITHOS_TO_HDFS_FILE = 'test_file_pithos_to_hdfs.txt'
DEST_PITHOS_TO_HDFS_FILE = 'test_file_hdfs_from_pithos.txt'

# Get from Hdfs to Pithos
SOURCE_HDFS_TO_PITHOS_FILE = 'test_file_hdfs_to_pithos.txt'
DEST_HDFS_TO_PITHOS_FILE = 'test_file_pithos_from_hdfs.txt'

# Output directories in hdfs for wordcount
PITHOS_WORDCOUNT_DIR = 'WordCount_Pithos'
HDFS_WORDCOUNT_DIR = 'WordCount_HDFS'

SPARK_EXAMPLES = '/usr/lib/spark/examples/lib/spark-examples-*-cdh*-hadoop*-cdh*.jar'
SPARK_ECOSYSTEM_EXAMPLES = '/usr/local/spark/lib/spark-examples-1.3.1-hadoop2.4.0.jar'
CLOUDERA_HDFS_PATH = 'sudo -u hdfs /usr/bin/hdfs '
CLOUDERA_WORDCOUNT = 'jar /usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar wordcount '
CLOUDERA_HADOOP_PATH = 'sudo -u hdfs /usr/bin/hadoop '
WORDCOUNT = 'jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount '
HADOOP_PATH = '/usr/local/hadoop/bin/hadoop '
HDFS_PATH = '/usr/local/hadoop/bin/hdfs '
PIG_CLOUDERA_COMMAND = "sudo -u hdfs pig -e \"fs -mkdir pig_test_folder\""
PIG_TEST_FOLDER = 'pig_test_folder'
OOZIE_TEST_FOLDER = 'oozie_app'
OOZIE_COMMAND = 'sudo -u hdfs oozie job -oozie http://{0}:11000/oozie -config /tmp/job.properties -run'
OOZIE_ECOSYSTEM_COMMAND = '/usr/local/oozie/bin/oozie job -oozie http://{0}:11000/oozie -config /tmp/job.properties -run'
JOB_PROPERTIES_TEMPLATE = 'nameNode=hdfs://{0}:9000\njobTracker=http://{0}:8050\noozie.libpath=hdfs://{0}:9000/user/oozie/share/lib\noozie.wf.application.path=hdfs://{0}:9000/user/hdfs/oozie_app'
JOB_PROPERTIES_ECOSYSTEM_TEMPLATE = 'nameNode=hdfs://{0}:9000\njobTracker=http://{0}:8050\noozie.libpath=hdfs://{0}:9000/user/hduser/share/lib\noozie.wf.application.path=hdfs://{0}:9000/user/hduser/oozie_app'

HBASE_SCRIPT_PATH = '/usr/local/hbase/bin/hbaseTest.sh'