#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script run a wordcount job in an existing Hadoop cluster in ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
'''
import create_cluster
from create_cluster import *


def run_wordcount_hadoop(name):
    '''
    Connect as root to master node and download kamaki and needed dependencies.
    Then, connect as hduser, setup kamaki, download file from pithos and
    run a wordcount job with it. Return the number of times string !important
    is appearing in the output file. Delete pithos_file and every directory
    run_wordcount_hadoop created.
    '''
    ssh_client = establish_connect(name, 'root', '', 22)
    # Download and install kamaki
    exec_command(ssh_client, 'echo "deb http://apt.dev.grnet.gr wheezy/"'
                 ' >> /etc/apt/sources.list')
    exec_command(ssh_client, 'apt-get -y install curl')
    exec_command(ssh_client, 'curl https://dev.grnet.gr/files/'
                 'apt-grnetdev.pub|apt-key add - ')
    exec_command(ssh_client, 'apt-get update')
    exec_command_hadoop(ssh_client, 'apt-get -y install kamaki')
    ssh_client.close()

    os.system('kamaki user authenticate > ' + FILE_KAMAKI)
    output = subprocess.check_output("awk '/expires/{getline; print}' "
                                     + FILE_KAMAKI, shell=True)
    token = output.replace(" ", "")[3:-1]
    os.system('rm ' + FILE_KAMAKI)
    auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'

    hduser_pass = get_hduser_pass()
    ssh_client = establish_connect(name, 'hduser', hduser_pass, 22)
    # kamaki setup from hduser and download file from pithos
    exec_command(ssh_client, 'kamaki config set cloud.hduser.url ' + auth_url)
    exec_command(ssh_client, 'kamaki config set cloud.hduser.token ' + token,
                 'hide_output')

    exec_command_hadoop(ssh_client, 'kamaki file download WordCount/'
                        + PITHOS_FILE, extend_timeout=True)

    # Perform WordCount job

    exec_command(ssh_client, '/usr/local/hadoop/bin/hadoop dfs -mkdir '
                 '/hdfs/input')
    exec_command_hadoop(ssh_client, '/usr/local/hadoop/bin/hadoop dfs '
                        '-copyFromLocal ' + PITHOS_FILE + ' /hdfs/input',
                        extend_timeout=True)
    exec_command_hadoop(ssh_client, '/usr/local/hadoop/bin/hadoop jar '
                        '/usr/local/hadoop/hadoop-examples-1.*.jar wordcount '
                        '/hdfs/input /hdfs/output', extend_timeout=True)
    exec_command(ssh_client, '/usr/local/hadoop/bin/hadoop fs -copyToLocal '
                 '/hdfs/output/ $HOME/')

    # Find number of times that string [!important] appeared in the pithos file
    command = "cd output;grep -m 1 'important' p*"
    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
    stdout_hadoop = stdout.read()
    # Replace /t/r/n characters and remove spaces
    line = stdout_hadoop.translate(string.maketrans("\n\t\r", "   "))
    to_return_value = line.replace(" ", "")
    # Cleaning up and deleting directories and files
    exec_command_hadoop(ssh_client, 'rm elwiki-20140818-pages-meta'
                        '-current-5000000.xml')
    exec_command_hadoop(ssh_client, 'rm -r output')
    exec_command_hadoop(ssh_client, '/usr/local/hadoop/bin/hadoop dfs '
                        '-rmr /hdfs/output')
    exec_command_hadoop(ssh_client, '/usr/local/hadoop/bin/hadoop dfs '
                        '-rmr /hdfs/input')
    # Close the ssh connection
    ssh_client.close()
    # Return the wordcount value
    return int(to_return_value[-2:])


def test_wordcount():
    '''
    Test that runs wordcount job on an existing hadoop cluster.
    Must define existing fqdn of the master node.
    '''
    name = 'xxx'
    assert run_wordcount_hadoop(name) == 13


def main(opts):
    '''Calls wordcount_hadoop with arguments passed from command line'''
    wordcount_value = run_wordcount_hadoop(opts.name)
    logging.log(REPORT, 'Number of times string [!important] is appearing '
                'is: %d', wordcount_value)


if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog runs a wordcount job on a hadoop cluster in' \
                        'Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="MASTER NODE NAME",
                      help='The fully qualified domain name of master node')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')
    main(opts)
