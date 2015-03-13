#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script configures the communication between VMs in a ~okeanos
 cluster and installs python in every VM.

@author: Ioannis Stenos, Nick Vrionis
"""
import os
import logging
import paramiko
from time import sleep
import select
from celery import current_task
from cluster_errors_constants import error_hdfs_test_exit_status, const_truncate_limit, error_fatal
from okeanos_utils import parse_hdfs_dest

# Definitions of return value errors
from cluster_errors_constants import error_ssh_client, REPORT, \
    SUMMARY, ADD_TO_GET_PORT

# Global constants
MASTER_SSH_PORT = 22  # Port of master virtual machine for ssh connection
CHAN_TIMEOUT = 3600  # Paramiko channel timeout
CONNECTION_TRIES = 9    # Max number(+1) of connection attempts to a VM
HADOOP_HOME = '/usr/local/hadoop/bin/'


class HdfsRequest(object):
    """
    Class with the required methods for performing ftp/http file transfer to hdfs and checking for errors.
    """
    def __init__(self, opts):
        self.opts = opts
        self.full_path = self.opts['dest']
        self.ssh_client = establish_connect(self.opts['master_IP'], 'hduser', '',
                                   MASTER_SSH_PORT)

    def check_hdfs_path(self, dest, option):
        """
        Check if a path exists in Hdfs 0: exists, 1: doesn't exist
        """
        path_exists = self.exec_hadoop_command(dest, option)
        if option == ' -e ' and path_exists == 0:
            msg = ' File already exists. Aborting upload.'
            raise RuntimeError(msg)
        elif option == ' -d ' and path_exists != 0:
            return 1
        return path_exists

    def check_file(self):
        """
        Checks, depending on the value of check arg, if file exists in hdfs or has zero size.
        """
        filename = self.opts['source'].split("/")
        parsed_path = parse_hdfs_dest("(.+/)[^/]+$", self.opts['dest'])

        # if destination is directory, check if directory exists in hdfs,
        if parsed_path:
            # if directory path ends with filename, checking if both exist
            if self.check_hdfs_path(parsed_path, ' -d ') == 1:
                msg = ' Target directory does not exist. Aborting upload'
                raise RuntimeError(msg)
            if self.check_hdfs_path(self.opts['dest'], ' -d ') == 0:
                self.full_path += '/' + filename[len(filename)-1]
                return 0
            else:
                self.check_hdfs_path(self.opts['dest'], ' -e ')
        elif self.opts['dest'].endswith("/") and not self.opts['dest'].startswith("/"):
            # if only directory is given
            if self.check_hdfs_path(self.opts['dest'], ' -d ') == 1:
                msg = ' Target directory does not exist. Aborting upload'
                raise RuntimeError(msg)
            self.check_hdfs_path(self.opts['dest'] + filename[len(filename)-1], ' -e' )
            self.full_path += filename[len(filename)-1]
        # if destination is default directory /user/hduser, check if file exists in /user/hduser.
        else:
            self.check_hdfs_path(self.opts['dest'],' -e ')


    def exec_hadoop_command(self, dest, option, check=''):
        """

        :return: status of paramiko executed command.
        """
        check_cmd = HADOOP_HOME + 'hadoop fs -test' + option + dest
        try:
            status = exec_command(self.ssh_client, check_cmd)
        except RuntimeError, e:
            if e.args[1] == error_hdfs_test_exit_status:
                return 1
        if status == 0:
            if check == 'zero_size':
                rm_cmd = HADOOP_HOME + 'hadoop fs -rm ' + dest
                exec_command(self.ssh_client, rm_cmd)
                msg = ' Transfer to destination %s failed. ' % dest
                raise RuntimeError(msg)
            else:
                return 0

    def put_file_hdfs(self):
        """
        Put a file from ftp/hhtp to hdfs
        """

        try:
            put_cmd = ' wget --user=' + self.opts['user'] + ' --password=' + self.opts['password'] + ' ' +\
                      self.opts['source'] + ' -O - |' + HADOOP_HOME + 'hadoop fs -put - ' + self.opts['dest']
            put_cmd_status = exec_command(self.ssh_client, put_cmd, command_state='celery_task')
            self.exec_hadoop_command(self.full_path, ' -z ', check='zero_size')
            return put_cmd_status
        finally:
            self.ssh_client.close()



def reroute_ssh_prep(server, master_ip):
    """
    Creates list of host and ip-tables for reroute ssh to all slaves
    """
    hostname_master = master_ip
    list_of_hosts = []  # List of dicts with VM hostnames and their private IPs
    dict_s = {}  # Dictionary that will contain fully qualified domain names
    # and private ips temporarily for each machine. It will be appended
    # each time to list_of_hosts. List_of_hosts is the list that has every
    #  fqdn and private ip of the virtual machines.
    logging.log(SUMMARY, ' Configuring Yarn cluster node communication')
    master_VM_password = server[0]['adminPass']
    for s in server:
        if s['name'].split('-')[-1] == '1':  # Master vm
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': '192.168.0.2',
                      'port': 22, 'password': s['adminPass']}
            list_of_hosts.append(dict_s)
            # Pre-setup the port forwarding that will happen later
            get_ready_for_reroute(hostname_master, master_VM_password)
        else:
            # Every slave ip is increased by 1 from the private ip of the
            # previous slave.The first slave is increased by 1 from the
            # master ip which is 192.168.0.2.
            slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
            port = ADD_TO_GET_PORT+int(s['name'].split('-')[-1])
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': slave_ip,
                      'port': port, 'password': s['adminPass']}
            list_of_hosts.append(dict_s)

    # Port-forwarding now for every slave machine
    for vm in list_of_hosts[1:]:
        reroute_ssh_to_slaves(vm['port'], vm['private_ip'], hostname_master, vm['password'], master_VM_password)

    return list_of_hosts


def get_ready_for_reroute(hostname_master, password):
    """
    Runs pre-setup commands for port forwarding in master virtual machine.
    These commands are executed only.
    """
    ssh_client = establish_connect(hostname_master, 'root', password,
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'apt-get update')
        exec_command(ssh_client, 'apt-get -y install python')
        exec_command(ssh_client, 'echo 1 > /proc/sys/net/ipv4/ip_forward')
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth1 -j MASQUERADE')
        exec_command(ssh_client, 'iptables --table nat --append POSTROUTING '
                                 '--out-interface eth2 -j MASQUERADE')
        exec_command(ssh_client, 'iptables --append FORWARD --in-interface '
                                 'eth2 -j ACCEPT')
        # iptables commands to route Hdfs 9000 port traffic from master_VM public ip to
        # 192.168.0.2, which is the ip used in core-site.xml configuration.
        exec_command(ssh_client, 'iptables -t nat -A PREROUTING -p tcp --dport 9000'
                                 ' -j DNAT --to-destination 192.168.0.2:9000')
        exec_command(ssh_client, 'iptables -t nat -A POSTROUTING -p tcp -d 192.168.0.2 --dport 9000'
                                 ' -j SNAT --to-source ' + hostname_master)
    finally:
        ssh_client.close()


def exec_command(ssh, command, command_state=''):
    """
    Calls overloaded exec_command function of the ssh object given
    as argument. Command is the second argument and its a string.
    Command_state argument is used when running celery tasks and
    feedback is needed.
    """
    try:
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    except Exception, e:
        logging.exception(e.args)
        raise
    if command_state == 'celery_task':
        # Wait for the command to terminate
        while not stdout.channel.exit_status_ready():
            # Only update celery task state if there is data to read in the channel
            if stdout.channel.recv_ready():
                rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                if len(rl) > 0:
                    state = stdout.channel.recv(1024)
                    if len(state) >= const_truncate_limit:
                        state = state[:(const_truncate_limit-2)] + '..'
                    current_task.update_state(state=state)

    # get exit status of command executed and check it with check_command
    ex_status = stdout.channel.recv_exit_status()
    check_command_exit_status(ex_status, command)
    return ex_status


class mySSHClient(paramiko.SSHClient):
    """Class that inherits paramiko SSHClient"""
    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False):
        """
        Overload paramiko exec_command by adding a timeout.
        Timeout is needed because script hangs when there is not an answer
        from paramiko exec_command,e.g.in a disconnect.
        """
        chan = self._transport.open_session()
        if get_pty:
            chan.get_pty()
        chan.settimeout(CHAN_TIMEOUT)  # Add a timeout to the exec_command
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)
        return stdin, stdout, stderr


def check_command_exit_status(ex_status, command):
    """
    Checks the exit status of every command executed in virtual machines
    by paramiko exec_command.If the value is different from zero,it raises
    a RuntimeError exception.If the value is zero it logs the appropriate
    message.
    """
    if ex_status != 0:
            msg = ' Command %s failed with exit status: %d'\
                  % (command, ex_status)
            raise RuntimeError(msg, ex_status)
    else:
        logging.log(REPORT, ' Command: %s execute with exit status:%d',
                    command, ex_status)


def reroute_ssh_to_slaves(dport, slave_ip, hostname_master, password, master_VM_password):
    """
    For every slave vm in the cluster this function is called.
    Finishes the port forwarding and installs python for ansible
    in every machine. Arguments are the port and the private ip of
    the slave vm.
    """
    ssh_client = establish_connect(hostname_master, 'root', master_VM_password,
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'iptables -A PREROUTING -t nat -i eth1 -p tcp'
                                 ' --dport '+str(dport)+' -j DNAT --to '
                                 + slave_ip + ':22')
        exec_command(ssh_client, 'iptables -A FORWARD -p tcp -d '
                                 + slave_ip + ' --dport 22 -j ACCEPT')
    finally:
        ssh_client.close()

    ssh_client = establish_connect(hostname_master, 'root', password, dport)
    try:
        exec_command(ssh_client, 'route add default gw 192.168.0.2')
        exec_command(ssh_client, 'apt-get update')
        exec_command(ssh_client, 'apt-get -y install python')

    finally:
        ssh_client.close()


def establish_connect(hostname, name, passwd, port):
    """
    Establishes an ssh connection with given hostname, username, password
    and port number.Tries to ping given hostname.If the ping is successfull
    it tries to ssh connect.If an ssh connection is succesful, returns an
    ssh object.If ssh connection fails or throws an exception,logs the error
    and tries to ping again.After a number of failed pings or failed ssh
    connections throws RuntimeError exception.Number of tries is ten.
    """
    try:
        ssh = mySSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    except:
        msg = " Failed creating ssh.client for paramiko"
        raise RuntimeError(msg, error_ssh_client)
    i = 0
    while True:
        response = os.system("ping -c1 -w4 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            try:
                logging.log(REPORT, ' Ping %s:%s', hostname, port)
                ssh.connect(hostname, username=name, password=passwd,
                            port=port)
                logging.log(REPORT, " ssh as %s to %s:%s",
                            name, hostname, str(port))
                return ssh
            except Exception, e:
                logging.warning(e.args)
                logging.warning(" Cannot ssh as %s to %s:%s, trying again",
                                name, hostname, str(port))
                if i > CONNECTION_TRIES:
                    break
                i = i+1
                sleep(1)
        else:
            if i > CONNECTION_TRIES:
                break
            logging.warning(' Cannot ping %s:%s, trying again',
                            hostname, str(port))
            i = i+1
            sleep(1)
    ssh.close()
    msg = " Failed connecting as %s to %s:%s" % \
        (name, hostname, str(port))
    raise RuntimeError(msg, error_ssh_client)