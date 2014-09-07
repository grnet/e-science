#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script checks a hadoop cluster and run a pi job in ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
'''
import create_cluster
from create_cluster import *
import subprocess


'''def test_run_pi_2_10000():

    name = 'snf-581845.vm.okeanos.grnet.gr'
    assert check_hadoop_cluster_and_run_pi(name, 2, 10000) == \
        3.14280000000000000000


def test_run_pi_2_100000():

    name = 'snf-580910.vm.okeanos.grnet.gr'
    assert check_hadoop_cluster_and_run_pi(name, 2, 100000) == \
        3.14118000000000000000


def test_run_pi_10_100000():

    name = 'snf-580910.vm.okeanos.grnet.gr'
    assert check_hadoop_cluster_and_run_pi(name, 10, 100000) == \
        3.14155200000000000000'''


def test_create_cluster_low():

    os.system('kamaki user authenticate > ' + FILE_KAMAKI)
    output = subprocess.check_output("awk '/expires/{getline; print}' " + FILE_KAMAKI, shell=True)
    token = output.replace(" ", "")[3:-1]
    assert create_cluster('hadoop', 3, 2, 1024, 5,
                          'ext_vlmc', 2, 512, 5, token,
                          'Debian Base') == 3.14280000000000000000


'''def test_create_cluster_medium():

    os.system('kamaki user authenticate > ' + FILE_KAMAKI)
    output = subprocess.check_output("awk '/expires/{getline; print}' " + FILE_KAMAKI, shell=True)
    token = output.replace(" ", "")[3:-1]
    assert create_cluster('hadoop', 4, 4, 4096, 20,
                          'ext_vlmc', 4, 4096, 20, token,
                          'Debian Base') == 3.14280000000000000000'''


'''def test_create_cluster_high():

    os.system('kamaki user authenticate > ' + FILE_KAMAKI)
    output = subprocess.check_output("awk '/expires/{getline; print}' " + FILE_KAMAKI, shell=True)
    token = output.replace(" ", "")[3:-1]
    assert create_cluster('hadoop', 9, 4, 4096, 20,
                          'ext_vlmc', 2, 2048, 20, token,
                          'Debian Base') == 3.14280000000000000000'''



def main(opts):
    '''
    The main function first establish ssh connection and then calls
    check_hadoop_cluster_and_run_pi.
    '''
    check_hadoop_cluster_and_run_pi('snf-581716.vm.okeanos.grnet.gr',
                                    2, 10000)


if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog checks a hadoop cluster and runs a job on' \
                        'Synnefo w. kamaki'

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
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')
    main(opts)
