#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script destroys a virtual cluster in synnefo.

@author: Ioannis Stenos, Nick Vrionis
'''
from sys import argv
from create_cluster import destroy_cluster
import logging
from optparse import OptionParser


def main(opts):
    '''
    The main function calls the destroy cluster with cluster_name and
    auth token given.
    '''
    cluster_name = opts.name
    auth = opts.token
    destroy_cluster(cluster_name, auth)

if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deletes a cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="CLUSTER NAME",
                      help='The name of the cluster')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')
    
    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(25, "REPORT")
    logger = logging.getLogger("report")



    
    logging_level = 25
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging_level, datefmt='%H:%M:%S')
    main(opts)
