#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script checks a yarn cluster and run a pi job in ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
'''

import re
import os
import sys
import nose
import logging
import paramiko
from time import sleep
from ConfigParser import RawConfigParser, NoSectionError
from os.path import join, dirname
sys.path.append('/home/developer/e-science')
from reroute_ssh import *
#GLobal constants
MASTER_SSH_PORT = 22  # Port of master virtual machine for ssh connection
CONNECTION_TRIES = 9  # Max number (+1)of connection attempts to a VM
REPORT = 25  # Define logging level of REPORT
CHAN_TIMEOUT = 360  # Paramiko channel timeout
FILE_RUN_PI = 'temp_file.txt'  # File used from pi function to write stdout

def exec_command(ssh_client, command):
    '''
    Exec_command for the run_pi.
    This one is used because for this method we want to see the output
    in report logging level and not in debug. 
    '''
    try:
        # This is for every other command of pi and wordcount
        stdin, stdout, stderr = ssh_client.exec_command(command,
                                                            get_pty=True)
        stdout_hadoop = stdout.read()
        # For pi command. Writes stdout to a file so we get the pi value
        if " pi " in command:
            with open(FILE_RUN_PI, 'w') as file_out:
                file_out.write(stdout_hadoop)
    except Exception, e:
        logging.exception(e.args)
        raise
    logging.log(REPORT, '%s %s', stdout_hadoop, stderr.read())
    ex_status = stdout.channel.recv_exit_status()
    check_command_exit_status(ex_status, command)


def check_string(to_check_file, to_find_str):
    '''
    Search the string passed as argument in the to_check file.
    If string is found, returns the whole line where the string was
    found. Function is used by the run_pi function.
    '''
    with open(to_check_file, 'r') as f:
        found = False
        for line in f:
            if re.search(to_find_str, line):
                return line
        if not found:
            logging.warning('The line %s cannot be found!', to_find_str)


def run_pi(pi_map, pi_sec):
    '''Runs a pi job'''
    #hduser_pass = get_hduser_pass()
    parser = RawConfigParser()
    config_file = join(dirname(dirname(dirname(__file__))), '.private/.config.txt')
    parser.read(config_file)
    master_ip = parser.get('cluster', 'master_ip')
    ssh_client = establish_connect(master_ip, 'hduser', '',
                                   MASTER_SSH_PORT)

    logging.log(REPORT, ' Running pi job')
    command = '/usr/local/hadoop/bin/hadoop jar' \
              ' /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi ' + \
              str(pi_map)+' '+str(pi_sec)
    exec_command(ssh_client, command)
    line = check_string(FILE_RUN_PI, "Estimated value of Pi is")
    os.system('rm ' + FILE_RUN_PI)
    ssh_client.close()
    return float(line[25:])


def test_run_pi_2_10000():

    assert run_pi(2, 10000) == 3.14280000000000000000

def test_run_pi_10_1000000():

    assert run_pi(10, 1000000) == 3.14158440000000000000

