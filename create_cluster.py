#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This script creates a virtual cluster and installs hadoop.

@author: Ioannis Stenos, Nick Vrionis
'''
import sys
from sys import argv
from os.path import abspath
from base64 import b64encode
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.pithos import PithosClient
from kamaki.clients.cyclades import CycladesNetworkClient
from kamaki.clients.image import ImageClient
from kamaki.clients.cyclades import CycladesClient
from optparse import OptionParser
from datetime import datetime
import paramiko
import time
from time import sleep
import os
import nose
import threading
import logging


error_syntax_clustersize = -1  # Definitions of different errors
error_syntax_cpu_master = -2
error_syntax_ram_master = -3
error_syntax_disk_master = -4
error_syntax_cpu_slave = -5
error_syntax_ram_slave = -6
error_syntax_disk_slave = -7
error_syntax_logging_level = -8
error_syntax_disk_template = -9
error_quotas_cyclades_disk = -10
error_quotas_cpu = -11
error_quotas_ram = -12
error_quotas_clustersize = -13
error_quotas_network = -14
error_flavor_id = -15
error_ssh_connection = -16
error_exec_command = -17
error_ready_reroute = -18
error_ssh_copyid_format_start_hadoop = -19
error_fatal = -20
error_cluster_not_exist = -21
error_user_quota = -22
error_flavor_list = -23
error_get_list_servers = -24
error_delete_server = -25
error_delete_network = -26
error_delete_float_ip = -27
error_get_network_quota = -28
error_create_network = -29
error_get_ip = -30
error_create_server = -31


MASTER_SSH_PORT = 22  # Port of master virtual machine for ssh connection
CHAN_TIMEOUT = 360  # Paramiko channel timeout
JOIN_THREADS_TIME = 1000  # Time to wait for threads to join
# Value to add machine name numbers and get slave port numbers
ADD_TO_GET_PORT = 9998
# How many times plus one it tries to connect to a virtual
# machine before aborting.
CONNECTION_TRIES = 9
REPORT = 25  # Define logging level of REPORT
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
# Href string characters without IpV4 public network id number
HREF_VALUE_MINUS_PUBLIC_NETWORK_ID = 56
threadLock = threading.Lock()
list_of_hosts = []  # List of virtual machine hostnames and their private ips


def exec_command_hadoop(ssh_client, command):
    '''
    exec_command for the check_hadoop_cluster, run_pi and wordcount.
    This one is used because for these methods we want to see the output
    in report logging level and not in debug.
    '''
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
    except Exception, e:
        logging.exception(e.args)
        raise
    logging.log(REPORT, '%s %s', stdout.read(), stderr.read())
    ex_status = stdout.channel.recv_exit_status()
    check_command_exit_status(ex_status, command)


def check_hadoop_cluster_and_run_pi(ssh_client, pi_map=2, pi_sec=10000):
    '''Checks hadoop cluster health and runs a pi job'''
    logging.log(REPORT, 'Checking Hadoop cluster')
    command = '/usr/local/hadoop/bin/hadoop dfsadmin -report'
    exec_command_hadoop(ssh_client, command)
    logging.log(REPORT, 'Running pi job')
    command = '/usr/local/hadoop/bin/hadoop jar' \
              ' /usr/local/hadoop/hadoop-examples-1.2.1.jar pi '+str(pi_map)+' '+str(pi_sec)
    exec_command_hadoop(ssh_client, command)


def destroy_cluster(cluster_name, token):
    '''
    Destroys cluster and deletes network and floating ip.Finds the machines
    that belong to the cluster that is requested to be destroyed and the
    floating ip of the master virtual machine and terminates them.Then
    deletes the network and the floating ip.
    '''
    servers_to_delete = []
    auth = check_credentials(token)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)
    nc = init_cyclades_netclient(endpoints['network'], token)
    try:
        list_of_servers = cyclades.list_servers(detail=True)
    except Exception:
        logging.exception('Could not get list of servers.'
                          'Cannot delete cluster')
        sys.exit(error_get_list_servers)

    for server in list_of_servers:  # Find the servers to be deleted
        if cluster_name == server['name'].rsplit('-', 1)[0]:
            servers_to_delete.append(server)
    # If the list of servers to delete is empty then abort
    if not servers_to_delete:
        logging.log(REPORT, " Cluster with name %s does not exist"
                    % cluster_name)
        sys.exit(error_cluster_not_exist)
    # Find the floating ip of master virtual machine
    for i in servers_to_delete[0]['attachments']:
        if i['OS-EXT-IPS:type'] == 'floating':
            float_ip_to_delete = i['ipv4']
    # Find network to be deleted
    try:
        list_of_networks = nc.list_networks()
        for net_work in list_of_networks:
            if net_work['name'] == \
                    servers_to_delete[0]['name'].rsplit('-', 1)[0]:
                network_to_delete_id = net_work['id']
    except Exception:
        logging.exception('Error in getting network to delete')
        sys.exit(error_delete_network)
    # Start cluster deleting
    try:
        for server in servers_to_delete:
            cyclades.delete_server(server['id'])
        logging.log(REPORT, ' There are %d servers to clean up'
                    % servers_to_delete.__len__())
    # Wait for every server of the cluster to be deleted
        for server in servers_to_delete:
            new_status = cyclades.wait_server(server['id'],
                                              current_status='ACTIVE',
                                              max_wait=300)
            logging.log(REPORT, ' Server %s is being %s', server['name'],
                        new_status)
            if new_status != 'DELETED':
                logging.error('Error deleting server %s' % server['name'])
                sys.exit(error_delete_server)
        logging.log(REPORT, ' Cluster %s is %s', cluster_name, new_status)
    # Find the correct network of deleted cluster and delete it
    except Exception:
        logging.exception('Error in deleting server')
        sys.exit(error_delete_server)

    try:
        nc.delete_network(network_to_delete_id)
        sleep(10)
        logging.log(REPORT, ' Network %s is deleted' %
                            net_work['name'])
    except Exception:
        logging.exception('Error in deleting network')
        sys.exit(error_delete_network)

    # Find the correct floating ip of deleted master machine and delete it
    try:
        for float_ip in nc.list_floatingips():
            if float_ip_to_delete == float_ip['floating_ip_address']:
                nc.delete_floatingip(float_ip['id'])
                logging.log(REPORT, ' Floating ip %s is deleted'
                            % float_ip['floating_ip_address'])
    except Exception:
        logging.exception('Error in deleting floating ip')
        sys.exit(error_delete_float_ip)


def configuration_bashrc(ssh_client):
    '''
    Configures .bashrc for hduser.Adds hadoop_home, java_home
    and useful aliases. Also adds java_home to hadoop-env.sh
    Takes as argument an ssh object returned from establish_connect
    '''
    exec_command(ssh_client, 'echo "export HADOOP_HOME=/usr/local/hadoop"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "export JAVA_HOME=/usr/lib/jvm/java-7-'
                             'oracle" >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "unalias fs &> /dev/null"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo \'alias fs="hadoop fs"\' >> .bashrc', 0)
    exec_command(ssh_client, 'echo "unalias hls &> /dev/null"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo \'alias hls="fs -ls"\' >> .bashrc', 0)
    sleep(1)
    exec_command(ssh_client, 'source ~/.bashrc', 0)
    sleep(1)
    exec_command(ssh_client, 'echo "export PATH=$PATH:$HADOOP_HOME/bin"'
                             ' >> $HOME/.bashrc', 0)
    exec_command(ssh_client, 'echo "export JAVA_HOME=/usr/lib/jvm/java-7-'
                             'oracle" >>'
                             ' /usr/local/hadoop/conf/hadoop-env.sh', 0)


def get_ready_for_reroute():
    '''
    Runs pre-setup commands for port forwarding in master virtual machine.
    These commands are executed only once before the threads start.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv4/ip_forward', 0)
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth1 -j MASQUERADE', 0)
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth2 -j MASQUERADE', 0)
        exec_command(ssh_client, 'iptables --append FORWARD --in-interface '
                                 'eth2 -j ACCEPT', 0)
    finally:
        ssh_client.close()


def reroute_ssh_to_slaves(dport, slave_ip):
    '''
    Every thread-slave virtual machine connects to master and setups
    its port forwarding rules with the port and private ip of the slave.
    Also connects to itself and adds the master as a default gateway,
    so the slave has internet access through master vm.
    Arguments are the port and the private ip of the slave vm.
    '''
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'iptables -A PREROUTING -t nat -i eth1 -p tcp'
                                 ' --dport '+str(dport)+' -j DNAT --to '
                                 + slave_ip + ':22', 0)
        exec_command(ssh_client, 'iptables -A FORWARD -p tcp -d '
                                 + slave_ip + ' --dport 22 -j ACCEPT', 0)
    finally:
        ssh_client.close()

    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', dport)
    try:
        exec_command(ssh_client, 'route add default gw 192.168.0.2', 0)

    finally:
        ssh_client.close()


class myThread (threading.Thread):
    '''
    Subclass of Thread.
    Run function calls creat_single_hadoop
    '''
    def __init__(self, threadID, name, vm):
        threading.Thread.__init__(self)
        self.threadID = threadID  # Ranges from 1 to clustersize
        self.name = name  # Fully qualified domain name of each vm
        self.vm = vm  # member of the server list returned by create_server

    def run(self):
        logging.log(REPORT, "Starting %s thread ", self.name)
        try:
            creat_single_hadoop_cluster(self.vm)
        except Exception, e:
            logging.exception(e.args)  # Catch an exception of one thread
            # Terminate program if a thread throws an exception
            os._exit(error_fatal)


class mySSHClient(paramiko.SSHClient):
    '''Class that inherits paramiko SSHClient'''
    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False):
        '''
        Overload paramiko exec_command by adding a timeout.
        Timeout is needed because script hangs when there is not an answer
        from paramiko exec_command,e.g.in a disconnect.
        '''
        chan = self._transport.open_session()
        if get_pty:
            chan.get_pty()
        chan.settimeout(CHAN_TIMEOUT)  # Add a timeout to the exec_command
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)
        return stdin, stdout, stderr


def create_multi_hadoop_cluster(server):
    '''
    Function that starts the threads.Creates thread objects,one for every
    virtual machine. Thread name is the fully qualified domain name of
    the virtual machine. Before the thread creation calls the
    get_ready_for_reroute to do a pre-setup for port forwarding
    in the master. Takes as argument the server list that is returned
    from create_cluster. We get from server list the fully qualified
    names and we find the virtual machine master.
    '''
    dict_s = {}  # Dictionary that will contain fully qualified domain names
    # and private ips temporarily for each machine. It will be appended
    # each time to list_of_hosts. List_of_hosts is the list that has every
    #  fqdn and private ip of the virtual machines.
    for s in server:
        if s['name'].split('-')[-1] == '1':  # Master vm
            # Hostname of master is used in every ssh connection.
            # So it is defined as global
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': '192.168.0.2'}
            global HOSTNAME_MASTER
            HOSTNAME_MASTER = s['SNF:fqdn']
            list_of_hosts.append(dict_s)
        else:
            # Every slave ip is increased by 1 from the private ip of the
            # previous slave.The first slave is increased by 1 from the
            # master ip which is 192.168.0.2.
            slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': slave_ip}
            list_of_hosts.append(dict_s)
    # Pre-setup the port forwarding that will happen later
    try:
        get_ready_for_reroute()
    except Exception, e:
        logging.exception(e.args)
        sys.exit(error_ready_reroute)
    i = 0
    # Threads are created, one for each virtual machine
    threads = []
    for s in server:
        t = myThread(i, s['SNF:fqdn'], s)
        t.start()
        threads.append(t)
        i = i+1

    for t in threads:
        t.join(JOIN_THREADS_TIME)
    # Wait for all threads to complete
    ssh_client = establish_connect(HOSTNAME_MASTER, 'hduser',
                                   'hduserpass', MASTER_SSH_PORT)
    # Copy ssh public key from master to every slave
    # Needed for passwordless ssh in hadoop
    try:
        for vm in list_of_hosts:
            if vm['private_ip'] != '192.168.0.2':
                exec_command(ssh_client, 'ssh-copy-id -i $HOME/.ssh/id_rsa.pub'
                             ' hduser@'+vm['fqdn'].split('.', 1)[0], 2)
        logging.log(REPORT, " Hadoop is installed and configured")
        format_and_start_hadoop(ssh_client)
        #check_hadoop_cluster_and_run_pi(ssh_client)
    except Exception, e:
        logging.error(e.args)
        sys.exit(error_ssh_copyid_format_start_hadoop)
    finally:
        ssh_client.close()


def format_and_start_hadoop(ssh_client):
    '''
    Runs the commands needed to format the hadoop cluster
    and then start the hadoop daemons.Takes as argument an ssh object
    returned from establish_connect.
    '''
    logging.log(REPORT, ' Formating hadoop')
    exec_command(ssh_client, '/usr/local/hadoop/bin/hadoop'
                             ' namenode -format', 0)
    logging.log(REPORT, ' Starting hadoop')
    exec_command(ssh_client, '/usr/local/hadoop/bin/start-dfs.sh', 3)
    exec_command(ssh_client, '/usr/local/hadoop/bin/start-mapred.sh', 0)
    logging.log(REPORT, ' Hadoop has started')


def creat_single_hadoop_cluster(s):
    '''
    Splits the threads. Master thread calls install_hadoop with port 22.
    Slave ports and slave_ips are defined by the last number in their name.
    10000 is the first slave port and 192.168.0.3 the first private slave ip.
    By adding 1 to the port and ip we have the next slave port and ip.
    There is a thread lock before reroute.That is because sometimes iptables
    fails from threads giving the command at the same time.
    The error is: resource temporarily unavailable.After the lock
    each slave thread calls install hadoop with its port.
    Argument s is an element of the server list returned from create_cluster
    '''
    if s['name'].split('-')[-1] == '1':  # Master virtual machine
        install_hadoop(MASTER_SSH_PORT)
    else:  # Slave virtual machines
        # Forwarding Ports are 10000,10001, etc for every slave vm
        port = ADD_TO_GET_PORT+int(s['name'].split('-')[-1])
        slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
        # reroute_ssh_to_slaves should be executed by one thread at a time
        try:
            threadLock.acquire()
            reroute_ssh_to_slaves(port, slave_ip)
        except Exception, e:
            logging.exception(e.args)
            # Exit is here because otherwise another thread could
            # get lock before exit and the lock wouldnt get released.
            os._exit(error_fatal)
        finally:
            threadLock.release()

        install_hadoop(port)


def check_command_exit_status(ex_status, command):
    '''
    Checks the exit status of every command executed in virtual machines
    by paramiko exec_command.If the value is different from zero,it raises
    a RuntimeError exception.If the value is zero it logs the appropriate
    message.
    '''
    if ex_status != 0:
            logging.error('Command %s failed to execute with exit status: %d',
                          command, ex_status)
            logging.error('Program shutting down')
            msg = 'Command %s failed with exit status: %d'\
                  % (command, ex_status)
            raise RuntimeError(msg)
    else:
        logging.log(REPORT, ' Command: %s execute with exit status:%d',
                    command, ex_status)


def exec_command(ssh, command, check_id):
    '''
    Calls overloaded exec_command function of the ssh object given
    as argument. Command is the second argument and its a string.
    check_id is used for commands that need additional input after
    exec_command, e.g. ssh-keygen needs [enter] to save keys.
    '''
    try:
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    except Exception, e:
        logging.exception(e.args)
        raise
    if check_id == 1:  # For ssh-keygen
        stdin.flush()
        stdin.write('\n')
        stdin.flush()
        # prints stdout of execcommand
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)

    elif check_id == 2:  # For ssh-copy-id
        stdin.flush()
        sleep(3)  # Sleep is necessary for stdin to read yes
        stdin.write('yes\n')
        sleep(3)  # Sleep is necessary for stdin to read hduser pass
        stdin.write('hduserpass\n')
        stdin.flush()
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)

    elif check_id == 3:  # For ssh to master after starting hadoop
        stdin.flush()
        sleep(10)  # Sleep is necessary for stdin to read yes
        stdin.write('yes\n')
        stdin.flush()
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)

    else:
        logging.debug('%s %s', stdout.read(), stderr.read())
        # get exit status of command executed and check it with check_command
        ex_status = stdout.channel.recv_exit_status()
        check_command_exit_status(ex_status, command)


def install_hadoop(port):
    '''
    Function that is executed by every thread.
    Depending on the port argument, it connects
    and installs hadoop to the vm defined by the
    port.First,it connects with master as root.
    Runs apt-get update,installs sudo. Then calls
    other important functions and disconnects as root.
    Reconnects as hduser and configures bashrc
    '''
    # Connect as root and install sudo
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', port)
    try:
        exec_command(ssh_client, 'apt-get update;apt-get install sudo', 0)

        install_python_and_java(ssh_client)  # Install java
        add_hduser_disable_ipv6(ssh_client)  # Add hduser and disable ipv6
        configuration_hosts_file(ssh_client)  # Configures /etc/hosts file
    finally:
        ssh_client.close()

    ssh_client = establish_connect(HOSTNAME_MASTER, 'hduser', 'hduserpass',
                                   port)  # Reconnect as hduser
    try:
        connect_as_hduser_conf_ssh(ssh_client)
        configuration_bashrc(ssh_client)  # Configures .bashrc for hduser
        hadoop_xml_conf(ssh_client)  # Creates the needed xml files for hadoop
        if port == MASTER_SSH_PORT:  # For Master vm only
            configure_master_slaves(ssh_client)
    finally:
        ssh_client.close()


def configure_master_slaves(ssh_client):
    '''
    Configures two files only in the master virtual machine.
    The files are $Hadoop_HOME/conf/masters and
    $Hadoop_HOME/conf/slaves.
    '''
    for vm in list_of_hosts:
        # Adds fully qualified domain names for master and slaves in
        # the masters and slaves files in hadoop/conf
        if vm['private_ip'] == '192.168.0.2':
            exec_command(ssh_client, 'echo "' + vm['fqdn'].split('.', 1)[0] +
                                     '"> /usr/local/hadoop/conf/masters', 0)
        else:
            exec_command(ssh_client, 'echo "' + vm['fqdn'].split('.', 1)[0] +
                                     '">> /usr/local/hadoop/conf/slaves', 0)

    #  Delete localhost from slaves file
    exec_command(ssh_client, 'sed -i".bak" "1d" /usr/local/hadoop'
                             '/conf/slaves', 0)


def hadoop_xml_conf(ssh_client):
    '''
    This function creates the three xml files hadoop needs to start.
    The default files are empty. The function removes the empty files
    and writes the new ones with everything configured.
    '''
    core_site = [r'<?xml version=\"1.0\"?>',
                 r'<?xml-stylesheet type=\"text/xsl\" '
                 'href=\"configuration.xsl\"?>',
                 r'<configuration>',
                 r'<property>',
                 r'<name>hadoop.tmp.dir</name>',
                 r'<value>/app/hadoop/tmp</value>',
                 r'<description>A base for other temporary'
                 ' directories.</description>',
                 r'</property>',
                 r'<property>',
                 r'<name>fs.default.name</name>',
                 r'<value>hdfs://'+HOSTNAME_MASTER.split('.', 1)[0]+':54310</value>',
                 r'</property>',
                 r'</configuration>']

    mapred_site = [r'<?xml version=\"1.0\"?>',
                   r'<?xml-stylesheet type=\"text/xsl\" '
                   'href=\"configuration.xsl\"?>',
                   r'<configuration>',
                   r'<property>',
                   r'<name>mapred.job.tracker</name>',
                   r'<value>'+HOSTNAME_MASTER.split('.', 1)[0]+':54311</value>',
                   r'<description>The host and port that'
                   ' the MapReduce job tracker runs',
                   r'and reduce task.',
                   r'</description>',
                   r'</property>',
                   r'</configuration>']

    hdfs_site = [r'<?xml version=\"1.0\"?>',
                 r'<?xml-stylesheet type=\"text/xsl\" '
                 'href=\"configuration.xsl\"?>',
                 r'<configuration>',
                 r'<property>',
                 r'<name>dfs.replication</name>',
                 r'<value>2</value>',
                 r'<description>Default block replication.',
                 r'The actual number of replications can be'
                 ' specified when the file is created.',
                 r'The default is used if replication is not'
                 ' specified in create time.',
                 r'</description>',
                 r'</property>',
                 r'</configuration>']

    # Create a temp directory needed for hadoop and gives nesessary ownership
    exec_command(ssh_client, 'sudo mkdir -p /app/hadoop/tmp', 0)
    exec_command(ssh_client, 'sudo chown hduser:hadoop /app/hadoop/tmp', 0)
    # Remove the default xml files
    exec_command(ssh_client, 'rm -f /usr/local/hadoop/conf/core-site.xml', 0)
    exec_command(ssh_client, 'rm -f /usr/local/hadoop/conf/mapred-site.xml', 0)
    exec_command(ssh_client, 'rm -f /usr/local/hadoop/conf/hdfs-site.xml', 0)
    # Create and configure the xml files so hadoop
    # can format and start its daemons.
    for l in core_site:
        exec_command(ssh_client, 'echo "'+l+'" >> /usr/local/'
                                 'hadoop/conf/core-site.xml', 0)
    for l in mapred_site:
        exec_command(ssh_client, 'echo "'+l+'" >> /usr/local'
                                 '/hadoop/conf/mapred-site.xml', 0)
    for l in hdfs_site:
        exec_command(ssh_client, 'echo "'+l+'" >> /usr/local'
                                 '/hadoop/conf/hdfs-site.xml', 0)


def configuration_hosts_file(ssh_client):
    '''
    Configures /etc/hosts file for every machine as root.
    Adds hostnames and private ip addresses.
    Also deletes the second line of /etc/hosts
    so there can be only one private ip for each virtual machine.
    '''
    for machine in list_of_hosts:
        exec_command(ssh_client, 'sed -i".bak" "2d" /etc/hosts', 0)
        exec_command(ssh_client, 'echo '
                     '"' + machine['private_ip'] + '     ' +
                     machine['fqdn'].split('.', 1)[0]+'" >> /etc/hosts', 0)


def establish_connect(hostname, name, passwd, port):
    '''
    Establishes an ssh connection with given hostname, username, password
    and port number.Tries to ping given hostname.If the ping is successfull
    it tries to ssh connect.If an ssh connection is succesful, returns an
    ssh object.If ssh connection fails or throws an exception,logs the error
    and tries to ping again.After a number of failed pings or failed ssh
    connections throws RuntimeError exception.Number of tries is ten.
    '''
    try:
        ssh = mySSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    except:
        logging.error("Failed creating ssh.client")
        raise
    i = 0
    while True:
        response = os.system("ping -c1 -w4 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            try:
                logging.log(REPORT, ' Pinged %s machine,trying to ssh connect',
                            hostname)
                ssh.connect(hostname, username=name, password=passwd,
                            port=port)
                logging.log(REPORT, " Success in ssh connect as %s to %s"
                            "at port %s", name, hostname, str(port))
                return ssh
            except Exception, e:
                logging.warning(e.args)
                logging.warning("Problem in ssh connection as %s to %s at port"
                                " %s trying again", name, hostname, str(port))
                if i > CONNECTION_TRIES:
                    break
                i = i+1
                sleep(1)
        else:
            if i > CONNECTION_TRIES:
                break
            logging.warning('Cannot ping %s machine in port %s, trying again',
                            hostname, str(port))
            i = i+1
            sleep(1)
    ssh.close()
    logging.error("Failed connecting as %s to %s at port %s",
                  name, hostname, str(port))
    logging.error("Program is shutting down")
    msg = 'Failed connecting to %s virtual machine' % hostname
    raise RuntimeError(msg)


def connect_as_hduser_conf_ssh(ssh_client):
    '''
    Executes the following commands to the machine ssh_client is connected.
    Creates ssh key for hduser, downloads hadoop from eu apache mirror
    and creates hadoop folder in usr/local, giving ownership and permissions
    to hduser.
    '''

    exec_command(ssh_client, 'ssh-keygen -t rsa -P "" ', 1)
    exec_command(ssh_client, 'cat /home/hduser/.ssh/id_rsa.pub >> /home/'
                             'hduser/.ssh/authorized_keys', 0)

    exec_command(ssh_client, 'wget www.eu.apache.org/dist/hadoop/common/'
                             'stable1/hadoop-1.2.1.tar.gz', 0)
    exec_command(ssh_client, 'sudo tar -xzf $HOME/hadoop-1.2.1.tar.gz', 0)
    exec_command(ssh_client, 'sudo mv hadoop-1.2.1 /usr/local/hadoop', 0)
    exec_command(ssh_client, 'cd /usr/local;sudo chown -R hduser:hadoop'
                             ' hadoop', 0)


def install_python_and_java(ssh_client):
    '''Installs oracle java 7'''
    #  exec_command(ssh_client, 'apt-get -y install python-software-'
    # 'properties', 0)... Python-software-properties was commented out
    exec_command(ssh_client, 'echo "deb http://ppa.launchpad.net/webupd8team/'
                             'java/ubuntu precise main" | tee /etc/apt/sources'
                             '.list.d/webupd8team-java.list;echo "deb-src '
                             'http://ppa.launchpad.net/webupd8team/java/ubuntu'
                             ' precise main" | tee -a /etc/apt/sources.list.d/'
                             'webupd8team-java.list', 0)
    exec_command(ssh_client, 'apt-key adv --keyserver keyserver.ubuntu.com --'
                             'recv-keys EEA14886;apt-get update;echo oracle-'
                             'java7-installer shared/accepted-oracle-license-'
                             'v1-1 select true | /usr/bin/debconf-set-'
                             'selections;apt-get -y install oracle-java7'
                             '-installer', 0)
    exec_command(ssh_client, 'apt-get install oracle-java7-set-default', 0)


def add_hduser_disable_ipv6(ssh_client):
    '''
    Creates hadoop group and hduser and
    gives them passwordless sudo to help with remaining procedure
    Also disables ipv6. Takes as argument an ssh object returned
    from establish_connect.
    '''
    exec_command(ssh_client, 'addgroup hadoop;echo "%hadoop ALL=(ALL)'
                             ' NOPASSWD: ALL " >> /etc/sudoers', 0)
    exec_command(ssh_client, 'adduser hduser --disabled-password --gecos "";'
                             'adduser hduser hadoop;echo "hduser:hduserpass" |'
                             ' chpasswd', 0)
    exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv6/conf/all/'
                             'disable_ipv6', 0)
    exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv6/conf/default/'
                             'disable_ipv6', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.all.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.default.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)
    exec_command(ssh_client, 'echo "net.ipv6.conf.lo.disable_ipv6 = 1"'
                             ' >> /etc/sysctl.conf', 0)


def check_credentials(token, auth_url='https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0'):
    '''Identity,Account/Astakos. Test authentication credentials'''
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        logging.error('Authentication failed with url %s and token %s' % (
                      auth_url, token))
        raise
    logging.log(REPORT, ' Authentication verified')
    return auth


def endpoints_and_user_id(auth):
    '''
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    '''
    logging.log(REPORT, ' Get the endpoints')
    try:
        endpoints = dict(
            astakos=auth.get_service_endpoints('identity')['publicURL'],
            cyclades=auth.get_service_endpoints('compute')['publicURL'],
            pithos=auth.get_service_endpoints('object-store')['publicURL'],
            plankton=auth.get_service_endpoints('image')['publicURL'],
            network=auth.get_service_endpoints('network')['publicURL']
            )
        user_id = auth.user_info['id']
    except ClientError:
        logging.error('Failed to get endpoints & user_id from identity server')
        raise
    return endpoints, user_id


def init_pithos(endpoint, token, user_id):
    '''
    Object-store / Pithos+.Not used in the script,
    but left for future use
    '''
    logging.log(REPORT, ' Initialize Pithos+ client and'
                'set account to user uuid')
    try:
        return PithosClient(endpoint, token, user_id)
    except ClientError:
        logging.error('Failed to initialize a Pithos+ client')
        raise


def upload_image(pithos, container, image_path):
    '''
    Pithos+/Upload Image
    Not used in the script,but left for future use
    '''
    logging.log(REPORT, ' Create the container "images" and use it')
    try:
        pithos.create_container(container, success=(201, ))
    except ClientError as ce:
        if ce.status in (202, ):
            logging.error('Container %s already exists' % container)
        else:
            logging.error('Failed to create container %s' % container)
            raise
    pithos.container = container

    logging.log(REPORT, ' Upload to "images"')
    with open(abspath(image_path)) as f:
        try:
            pithos.upload_object(
                image_path, f)
        except ClientError:
            logging.error('Failed to upload file %s to container %s' % (
                image_path, container))
            raise


def init_cyclades_netclient(endpoint, token):
    '''
    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating ip
    '''
    logging.log(REPORT, ' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize cyclades network client')
        raise


def init_plankton(endpoint, token):
    '''
    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    '''
    logging.log(REPORT, ' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize the Image client')
        raise


def register_image(plankton, name, user_id, container, path, properties):
    '''
    Image/Plankton.Registers image from Pithos in Plankton.Not used
    but left for future use
    '''
    image_location = (user_id, container, path)
    logging.log(REPORT, ' Register the image')
    try:
        return plankton.register(name, image_location, properties)
    except ClientError:
        logging.error('Failed to register image %s' % name)
        raise


def init_cyclades(endpoint, token):
    '''
    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    '''
    logging.log(REPORT, ' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        logging.error('Failed to initialize cyclades client')
        raise


class Cluster(object):
    '''
    Cluster class represents an entire cluster.Instantiation of cluster gets
    the following arguments: A CycladesClient object,a name-prefix for the
    cluster,the flavors of master and slave machines,the image id of their OS,
    the size of the cluster,a CycladesNetworkClient object and a AstakosClient
    object.
    '''
    def __init__(self, cyclades, prefix, flavor_id_master, flavor_id_slave,
                 image_id, size, net_client, auth_cl):
        self.client = cyclades
        self.nc = net_client
        self.prefix, self.size = prefix, int(size)
        self.flavor_id_master, self.auth = flavor_id_master, auth_cl
        self.flavor_id_slave, self.image_id = flavor_id_slave, image_id

    def get_flo_net_id(self, list_public_networks):
        '''
        Gets an Ipv4 floating network id from the list of public networks Ipv4
        and Ipv6. Takes the href value and removes first 56 characters.
        The number that is left is the public network id
        '''
        float_net_id = 0
        for lst in list_public_networks:
            if(lst['status'] == 'ACTIVE' and
               lst['name'] == 'Public IPv4 Network'):
                    float_net_id = lst['links'][0]['href']
                    break

        try:
            return float_net_id[HREF_VALUE_MINUS_PUBLIC_NETWORK_ID:]
        except TypeError:
            logging.error('Floating Network Id could not be found')
            raise

    def _personality(self, ssh_keys_path='', pub_keys_path=''):
        '''Personality injects ssh keys to the virtual machines we create'''
        personality = []
        if pub_keys_path:
            with open(abspath(pub_keys_path)) as f:
                personality.append(dict(
                    contents=b64encode(f.read()),
                    path='/root/.ssh/authorized_keys',
                    owner='root', group='root', mode=0600))
        if ssh_keys_path or pub_keys_path:
                personality.append(dict(
                    contents=b64encode('StrictHostKeyChecking no'),
                    path='/root/.ssh/config',
                    owner='root', group='root', mode=0600))
        return personality

    def check_network_quota(self):
        '''
        Checks if the user quota is enough to create a new private network
        Subtracts the number of networks used and pending from the max allowed
        number of networks
        '''
        try:
            dict_quotas = self.auth.get_quotas()
        except Exception:
            logging.exception('Error in getting user network quota')
            sys.exit(error_get_network_quota)
        limit_net = dict_quotas['system']['cyclades.network.private']['limit']
        usage_net = dict_quotas['system']['cyclades.network.private']['usage']
        pending_net = \
            dict_quotas['system']['cyclades.network.private']['pending']
        available_networks = limit_net-usage_net-pending_net
        if available_networks >= 1:
            logging.log(REPORT, ' Private Network quota is ok')
            return
        else:
            logging.error('Private Network quota exceeded')
            sys.exit(error_quotas_network)

    def create(self, ssh_k_path='', pub_k_path='', server_log_path=''):
        '''
        Creates a cluster of virtual machines using the Create_server method of
        CycladesClient.
        '''
        logging.log(REPORT, ' Create %s servers prefixed as %s',
                    self.size, self.prefix)
        servers = []
        empty_ip_list = []
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        # Names the master machine with a timestamp and a prefix name
        # plus number 1
        server_name = '%s%s%s%s%s' % (date_time, '-', self.prefix, '-', 1)
        # Name of the network we will request to create
        net_name = date_time + '-' + self.prefix
        self.check_network_quota()
        # Creates network
        try:
            new_network = self.nc.create_network('MAC_FILTERED', net_name)
        except Exception:
            logging.exception('Error in creating network')
            sys.exit(error_create_network)
        # Gets list of floating ips
        try:
            list_float_ips = self.nc.list_floatingips()
        except Exception:
            logging.exception('Error getting list of floating ips')
            sys.exit(error_get_ip)
        # If there are existing floating ips,we check if there is any free or
        # if all of them are attached to a machine
        if len(list_float_ips) != 0:
            for float_ip in list_float_ips:
                if float_ip['instance_id'] is None:
                    break
                else:
                    count = count+1
                    if count == len(list_float_ips):
                        try:
                            self.nc.create_floatingip(list_float_ips
                                                      [count-1]
                                                      ['floating_network_id'])
                        except ClientError:
                            logging.exception('Cannot create new ip')
                            sys.exit(error_get_ip)
        else:
            # No existing ips,so we create a new one
            # with the floating  network id
            try:
                pub_net_list = self.nc.list_networks()
                float_net_id = self.get_flo_net_id(pub_net_list)
                self.nc.create_floatingip(float_net_id)
            except Exception:
                logging.exception('Error in creating float ip')
                sys.exit(error_get_ip)
        logging.log(REPORT, ' Wait for %s servers to built', self.size)

        # Creation of master server

        try:
            servers.append(self.client.create_server(
                server_name, self.flavor_id_master, self.image_id,
                personality=self._personality(ssh_k_path, pub_k_path)))
        except Exception:
            logging.exception('Error creating master virtual machine'
                              % server_name)
            sys.exit(error_create_server)
        # Creation of slave servers
        for i in range(2, self.size+1):
            try:

                server_name = '%s%s%s%s%s' % (date_time,
                                              '-', self.prefix, '-', i)
                servers.append(self.client.create_server(
                    server_name, self.flavor_id_slave, self.image_id,
                    personality=self._personality(ssh_k_path, pub_k_path),
                    networks=empty_ip_list))

            except Exception:
                logging.exception('Error creating server %s' % server_name)
                sys.exit(error_create_server)
        # We put a wait server for the master here,so we can use the
        # server id later and the slave start their building without
        # waiting for the master to finish building
        try:
            new_status = self.client.wait_server(servers[0]['id'],
                                                 max_wait=300)
            logging.log(REPORT, ' Status for server %s is %s',
                        servers[0]['name'], new_status)
            # Create a subnet for the virtual network between master
            #  and slaves along with the ports needed
            self.nc.create_subnet(new_network['id'], '192.168.0.0/24',
                                  enable_dhcp=True)
            port_details = self.nc.create_port(new_network['id'],
                                               servers[0]['id'])
            self.nc.wait_port(port_details['id'], max_wait=300)
            # Wait server for the slaves, so we can use their server id
            # in port creation
            for i in range(1, self.size):
                new_status = self.client.wait_server(servers[i]['id'],
                                                     max_wait=300)
                logging.log(REPORT, ' Status for server %s is %s',
                            servers[i]['name'], new_status)
                port_details = self.nc.create_port(new_network['id'],
                                                   servers[i]['id'])
                self.nc.wait_port(port_details['id'], max_wait=300)
        except Exception:
            logging.exception('Error in finalizing cluster creation')
            sys.exit(error_create_server)

        if server_log_path:
            logging.info(' Store passwords in file %s', server_log_path)
            with open(abspath(server_log_path), 'w+') as f:
                from json import dump
                dump(servers, f, indent=2)
        return servers


def get_flavor_id(cpu, ram, disk, disk_template, cycladesclient):
    '''Return the flavor id based on cpu,ram,disk_size and disk template'''
    try:
        flavor_list = cycladesclient.list_flavors(True)
    except Exception:
        logging.exception('Could not get list of flavors')
        sys.exit(error_flavor_list)
    flavor_id = 0
    for flavor in flavor_list:
        if flavor['ram'] == ram and \
            flavor['SNF:disk_template'] == disk_template and \
                flavor['vcpus'] == cpu and \
                flavor['disk'] == disk:
            flavor_id = flavor['id']

    return flavor_id


def check_quota(auth, req_quotas):
    '''
    Checks if user quota are enough for what he needed to create the cluster.
    If limit minus (used and pending) are lower or
    higher than what user requests.Also divides with 1024*1024*1024
    to transform bytes to gigabytes.
     '''
    try:
        dict_quotas = auth.get_quotas()
    except Exception:
        logging.exception('Could not get user quota')
        sys.exit(error_user_quota)
    limit_cd = dict_quotas['system']['cyclades.disk']['limit']
    usage_cd = dict_quotas['system']['cyclades.disk']['usage']
    pending_cd = dict_quotas['system']['cyclades.disk']['pending']
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd) / Bytes_to_GB
    if available_cyclades_disk_GB < req_quotas['cyclades_disk']:
        logging.error('Cyclades disk out of limit')
        sys.exit(error_quotas_cyclades_disk)

    limit_cpu = dict_quotas['system']['cyclades.cpu']['limit']
    usage_cpu = dict_quotas['system']['cyclades.cpu']['usage']
    pending_cpu = dict_quotas['system']['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu
    if available_cpu < req_quotas['cpu']:
        logging.error('Cyclades cpu out of limit')
        sys.exit(error_quotas_cpu)

    limit_ram = dict_quotas['system']['cyclades.ram']['limit']
    usage_ram = dict_quotas['system']['cyclades.ram']['usage']
    pending_ram = dict_quotas['system']['cyclades.ram']['pending']
    available_ram = (limit_ram-usage_ram-pending_ram) / Bytes_to_MB
    if available_ram < req_quotas['ram']:
        logging.error('Cyclades ram out of limit')
        sys.exit(error_quotas_ram)
    limit_vm = dict_quotas['system']['cyclades.vm']['limit']
    usage_vm = dict_quotas['system']['cyclades.vm']['usage']
    pending_vm = dict_quotas['system']['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm
    if available_vm < req_quotas['vms']:
        logging.error('Cyclades vms out of limit')
        sys.exit(error_quotas_clustersize)
    logging.log(REPORT, ' Cyclades Cpu,Disk and Ram quotas are ok.')
    return


def main(opts):
    '''
    The main function of our script takes the arguments given and calls the
    check_quota function. Also, calls get_flavor_id to find the matching
    flavor_ids from the arguments given and finds the image id of the
    image given as argument. Then instantiates the Cluster and creates
    the virtual machine cluster of one master and clustersize-1 slaves.
    Calls the function to install hadoop to the cluster
    '''
    logging.log(REPORT, ' 1.Credentials  and  Endpoints')
    # Finds user public ssh key
    USER_HOME = os.path.expanduser('~')
    pub_keys_path = os.path.join(USER_HOME, ".ssh/id_rsa.pub")
    auth = check_credentials(opts.token, opts.auth_url)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], opts.token)
    flavor_master = get_flavor_id(opts.cpu_master, opts.ram_master,
                                  opts.disk_master, opts.disk_template,
                                  cyclades)
    flavor_slaves = get_flavor_id(opts.cpu_slave, opts.ram_slave,
                                  opts.disk_slave, opts.disk_template,
                                  cyclades)
    if flavor_master == 0 or flavor_slaves == 0:
        logging.error('Combination of cpu,ram,disk and disk_template does'
                      ' not match an existing id')

        sys.exit(error_flavor_id)
    # Total cpu,ram and disk needed for cluster
    cpu = opts.cpu_master + (opts.cpu_slave)*(opts.clustersize-1)
    ram = opts.ram_master + (opts.ram_slave)*(opts.clustersize-1)
    cyclades_disk = opts.disk_master + (opts.disk_slave)*(opts.clustersize-1)
    # The resources requested by user in a dictionary
    req_quotas = {'cpu': cpu, 'ram': ram, 'cyclades_disk': cyclades_disk,
                  'vms': opts.clustersize}
    check_quota(auth, req_quotas)
    plankton = init_plankton(endpoints['plankton'], opts.token)
    list_current_images = plankton.list_public(True, 'default')
    # Find image id of the arg given
    for lst in list_current_images:
        if lst['name'] == opts.image:
            chosen_image = lst

    logging.log(REPORT, ' 2.Create  virtual  cluster')
    cluster = Cluster(cyclades,
                      prefix=opts.name,
                      flavor_id_master=flavor_master,
                      flavor_id_slave=flavor_slaves,
                      image_id=chosen_image['id'],
                      size=opts.clustersize,
                      net_client=init_cyclades_netclient(endpoints['network'],
                                                         opts.token),
                      auth_cl=auth)

    server = cluster.create('', pub_keys_path, '')
    sleep(60)  # Sleep to wait for virtual machines become pingable
    logging.log(REPORT, ' 3.Create Hadoop cluster')
    create_multi_hadoop_cluster(server)  # Start the hadoop installation
    # Start cluster deleting
    # logging.log(REPORT, ' 4.Destroying Hadoop cluster')
    # destroy_cluster(server[0]['name'].rsplit('-', 1)[0], opts.token)


if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="CLUSTER NAME",
                      help='The prefix name of the cluster')
    parser.add_option('--clustersize',
                      action='store', type='int', dest='clustersize',
                      metavar="CLUSTER SIZE",
                      help='Number of virtual cluster nodes to create ')
    parser.add_option('--cpu_master',
                      action='store', type='int', dest='cpu_master',
                      metavar='CPU MASTER',
                      help='Number of cores for the master node')
    parser.add_option('--ram_master',
                      action='store', type='int', dest='ram_master',
                      metavar='RAM MASTER',
                      help='Size of RAM (in MB) for the master node')
    parser.add_option('--disk_master',
                      action='store', type='int', dest='disk_master',
                      metavar='DISK MASTER',
                      help='Disk size (in GB) for the master node')
    parser.add_option('--disk_template',
                      action='store', type='string', dest='disk_template',
                      metavar='DISK TEMPLATE',
                      help='Disk template (drbd, or ext_vlmc)')
    parser.add_option('--cpu_slave',
                      action='store', type='int', dest='cpu_slave',
                      metavar='CPU SLAVE',
                      help='Number of cores for the slave nodes')
    parser.add_option('--ram_slave',
                      action='store', type='int', dest='ram_slave',
                      metavar='RAM SLAVE',
                      help='Size of RAM (in MB) for the slave nodes')
    parser.add_option('--disk_slave',
                      action='store', type='int', dest='disk_slave',
                      metavar='DISK SLAVE',
                      help=' Disk size (in GB) for slave nodes')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')
    parser.add_option('--image',
                      action='store', type='string', dest='image',
                      metavar='IMAGE OS',
                      help='OS for the virtual machine cluster'
                           '.Default=Debian Base',
                      default='Debian Base')

    parser.add_option('--auth_url',
                      action='store', type='string', dest='auth_url',
                      metavar='AUTHENTICATION URL',
                      help='Synnefo authentication url'
                      '.Default=https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0',
                      default='https://accounts.okeanos.grnet.gr'
                              '/identity/v2.0')

    parser.add_option('--logging_level',
                      action='store', type='string', dest='logging_level',
                      metavar='LOGGING LEVEL',
                      help='Levels of logging messages:critical,'
                      'error,warning,report,info and debug'
                      '.Default is report',
                      default='report')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    levels = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'report': REPORT,
              'info': logging.INFO,
              'debug': logging.DEBUG}

    #  If clause to catch syntax error in logging argument
    if opts.logging_level not in ['critical', 'error', 'warning',
                                  'info', 'report', 'debug']:
        logging.error('invalid syntax for logging_level')
        sys.exit(error_syntax_logging_level)

    logging_level = levels[opts.logging_level]

    if opts.logging_level == 'debug':
        log_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(log_directory, "create_cluster_debug.log")
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging_level, datefmt='%H:%M:%S')

    if opts.clustersize <= 0:
        logging.error('invalid syntax for clustersize'
                      ',clustersize must be a positive integer')
        sys.exit(error_syntax_clustersize)

    if opts.cpu_master <= 0:
        logging.error('invalid syntax for cpu_master'
                      ', cpu_master must be a positive integer')
        sys.exit(error_syntax_cpu_master)

    if opts.ram_master <= 0:
        logging.error('invalid syntax for ram_master'
                      ', ram_master must be a positive integer')
        sys.exit(error_syntax_ram_master)

    if opts.disk_master <= 0:
        logging.error('invalid syntax for disk_master'
                      ', disk_master must be a positive integer')
        sys.exit(error_syntax_disk_master)

    if opts.cpu_slave <= 0:
        logging.error('invalid syntax for cpu_slave'
                      ', cpu_slave must be a positive integer')
        sys.exit(error_syntax_cpu_slave)

    if opts.ram_slave <= 0:
        logging.error('invalid syntax for ram_slave'
                      ', ram_slave must be a positive integer')
        sys.exit(error_syntax_ram_slave)

    if opts.disk_slave <= 0:
        logging.error('invalid syntax for disk_slave'
                      ', disk_slave must be a positive integer')
        sys.exit(error_syntax_disk_slave)

    if opts.disk_template not in ['drbd', 'ext_vlmc']:
        logging.error('invalid syntax for disk_template')
        sys.exit(error_syntax_disk_template)
    main(opts)
