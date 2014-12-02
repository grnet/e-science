#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script creates a virtual cluster on ~okeanos and installs Hadoop-Yarn
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''

import sys
import os
import logging
import subprocess
import paramiko
from optparse import OptionParser
from sys import argv
from time import sleep

# Definitions of return value errors
from cluster_errors_constants import error_ready_reroute, error_fatal, REPORT, \
    SUMMARY, ADD_TO_GET_PORT


# Global constants
MASTER_SSH_PORT = 22  # Port of master virtual machine for ssh connection
CHAN_TIMEOUT = 360  # Paramiko channel timeout
CONNECTION_TRIES = 9    # Max number(+1) of connection attempts to a VM
list_of_hosts = []  # List of dicts wit VM hostnames and their private IPs


def reroute_ssh_prep(server, master_ip):
    """
    Creates list of host and ip-tables for reroute ssh to all slaves
    """
    global HOSTNAME_MASTER
    HOSTNAME_MASTER = master_ip
    dict_s = {}  # Dictionary that will contain fully qualified domain names
    # and private ips temporarily for each machine. It will be appended
    # each time to list_of_hosts. List_of_hosts is the list that has every
    #  fqdn and private ip of the virtual machines.
    logging.log(SUMMARY, ' Configuring Yarn cluster node communication')
    for s in server:
        if s['name'].split('-')[-1] == '1':  # Master vm
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': '192.168.0.2',
                      'port': 22}
            global cluster_name
            cluster_name = s['name'].rsplit('-', 1)[0]
            list_of_hosts.append(dict_s)
        else:
            # Every slave ip is increased by 1 from the private ip of the
            # previous slave.The first slave is increased by 1 from the
            # master ip which is 192.168.0.2.
            slave_ip = '192.168.0.' + str(1 + int(s['name'].split('-')[-1]))
            port = ADD_TO_GET_PORT+int(s['name'].split('-')[-1])
            dict_s = {'fqdn': s['SNF:fqdn'], 'private_ip': slave_ip,
                      'port': port}
            list_of_hosts.append(dict_s)
    # Pre-setup the port forwarding that will happen later
    try:
        get_ready_for_reroute()
    except Exception, e:
        logging.exception(e.args)
        sys.exit(error_ready_reroute)
    # Port-forwarding now for every slave machine
    for vm in list_of_hosts:
        call_reroute_for_every_vm(vm)

    return list_of_hosts


def get_ready_for_reroute():
    """
    Runs pre-setup commands for port forwarding in master virtual machine.
    These commands are executed only.
    """
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
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
    finally:
        ssh_client.close()


def exec_command(ssh, command):
    """
    Calls overloaded exec_command function of the ssh object given
    as argument. Command is the second argument and its a string.
    check_command_id is used for commands that need additional input after
    exec_command, e.g. ssh-_after_hadoop needs yes[enter].
    """
    try:
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    except Exception, e:
        logging.exception(e.args)
        raise

    logging.debug('%s %s', stdout.read(), stderr.read())
    # get exit status of command executed and check it with check_command
    ex_status = stdout.channel.recv_exit_status()
    check_command_exit_status(ex_status, command)


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
            logging.error(' Command %s failed to execute with exit status: %d',
                          command, ex_status)
            logging.error('Program shutting down')
            msg = ' Command %s failed with exit status: %d'\
                  % (command, ex_status)
            raise RuntimeError(msg)
    else:
        logging.log(REPORT, ' Command: %s execute with exit status:%d',
                    command, ex_status)


def call_reroute_for_every_vm(vm):
    """Calls reroute_ssh_to_slaves function to finish port forwarding """
    if vm['port'] != 22:  # Not Master virtual machine
        # Slave virtual machines
        # Forwarding Ports are 10000,10001, etc for every slave vm
        try:
            reroute_ssh_to_slaves(vm['port'], vm['private_ip'])
        except Exception, e:
            logging.exception(e.args)
            os._exit(error_fatal)


def reroute_ssh_to_slaves(dport, slave_ip):
    """
    For every slave vm in the cluster this function is called.
    Finishes the port forwarding and installs python for ansible
    in every machine. Arguments are the port and the private ip of
    the slave vm.
    """
    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '',
                                   MASTER_SSH_PORT)
    try:
        exec_command(ssh_client, 'iptables -A PREROUTING -t nat -i eth1 -p tcp'
                                 ' --dport '+str(dport)+' -j DNAT --to '
                                 + slave_ip + ':22')
        exec_command(ssh_client, 'iptables -A FORWARD -p tcp -d '
                                 + slave_ip + ' --dport 22 -j ACCEPT')
    finally:
        ssh_client.close()

    ssh_client = establish_connect(HOSTNAME_MASTER, 'root', '', dport)
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
        logging.error(" Failed creating ssh.client")
        raise
    i = 0
    while True:
        response = os.system("ping -c1 -w4 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            try:
                logging.log(REPORT, ' Pinged %s machine,trying to ssh connect'
                            ' at port %s', hostname, port)
                ssh.connect(hostname, username=name, password=passwd,
                            port=port)
                logging.log(REPORT, " Success in ssh connect as %s to %s"
                            " at port %s", name, hostname, str(port))
                return ssh
            except Exception, e:
                logging.warning(e.args)
                logging.warning(" Cannot ssh connect as %s to %s at port"
                                " %s trying again", name, hostname, str(port))
                if i > CONNECTION_TRIES:
                    break
                i = i+1
                sleep(1)
        else:
            if i > CONNECTION_TRIES:
                break
            logging.warning(' Cannot ping %s machine at port %s, trying again',
                            hostname, str(port))
            i = i+1
            sleep(1)
    ssh.close()
    logging.error(" Failed connecting as %s to %s at port %s",
                  name, hostname, str(port))
    logging.error("Program is shutting down")
    msg = ' Failed connecting to %s virtual machine' % hostname
    raise RuntimeError(msg)


def main(opts):
    """
    The main function calls reroute_ssh_prep with the arguments given from
    command line.
    """
    reroute_ssh_prep(opts.server, opts.master_ip)

if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--server',
                      action='store', type='string', dest='server',
                      metavar="SERVER",
                      help='a list with information about the cluster(names and fqdn of the nodes)')
    parser.add_option('--master_ip',
                      action='store', type='string', dest='master_ip',
                      metavar="MASTER_IP",
                      help='it is the ipv4 of the master node ')

    opts, args = parser.parse_args(argv[1:])
    main(opts)
