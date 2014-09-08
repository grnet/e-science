#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script run a wordcount job in an existing Hadoop cluster in ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
'''
import create_cluster
from create_cluster import *


def test_wordcount():
    '''
    Test that runs wordcount job on an existing hadoop cluster.
    Must define existing fqdn of the master node.
    '''
    name = 'snf-582584.vm.okeanos.grnet.gr'
    assert wordcount_hadoop(name) == 13


def main(opts):
    '''Calls wordcount_hadoop from create_cluster'''
    wordcount_value = wordcount_hadoop(opts.name)
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
