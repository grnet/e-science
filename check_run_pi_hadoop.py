#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script checks a hadoop cluster and run a pi job in synnefo.

@author: Ioannis Stenos, Nick Vrionis
'''
from sys import argv
from create_cluster import check_hadoop_cluster_and_run_pi, establish_connect
import logging
from optparse import OptionParser


def main(opts):
    '''
    The main function first establish ssh connection and then calls
    check_hadoop_cluster_and_run_pi.
    '''
    ssh_client = establish_connect(opts.name, 'hduser', 'hduserpass', 22)
    try:
        check_hadoop_cluster_and_run_pi(ssh_client, opts.pifirst, opts.pisec)
    finally:
        ssh_client.close()


if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog checks a hadoop cluster and runs a job on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--master_name',
                      action='store', type='string', dest='name',
                      metavar="MASTER NODE NAME",
                      help='The fully qualified domain name of master node')
    parser.add_option('--pi_first',
                      action='store', type='int', dest='pifirst',
                      metavar='PI FIRST ARG',
                      help='pi job first argument.Default is 2',
                      default=2)
    parser.add_option('--pi_second',
                      action='store', type='int', dest='pisec',
                      metavar='PI SECOND ARG',
                      help='pi job second argument.Defaut is 10000',
                      default=10000)


    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(25, "REPORT")
    logger = logging.getLogger("report")



    
    logging_level = 25
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging_level, datefmt='%H:%M:%S')
    main(opts)
