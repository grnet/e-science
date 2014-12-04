#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script destroys a virtual cluster in synnefo.

@author: Ioannis Stenos, Nick Vrionis
'''
from sys import argv, exit
import logging
from optparse import OptionParser
from okeanos_utils import *
from cluster_errors_constants import *


def main(opts):
    '''
    The main function calls the destroy cluster with master_ip and
    auth token given.
    '''
    destroy_cluster(opts.token, opts.master_ip)

if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deletes a cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--master_ip',
                      action='store', type='string', dest='master_ip',
                      metavar="MASTER_IP",
                      help='The public ip of the master vm of the cluster')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logging.addLevelName(SUMMARY, "SUMMARY")
    logger = logging.getLogger("report")

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')

    if not opts.master_ip:
        logging.error('invalid syntax for master public ip')
        exit(error_syntax_token)

    if not opts.token:
        logging.error('invalid syntax for authentication token')
        exit(error_syntax_token)
    main(opts)
