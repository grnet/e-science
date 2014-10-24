#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This returns the quotas based on kamaki quota list.

@author: Ioannis Stenos, Nick Vrionis
'''

import os
import logging
from sys import argv
from os.path import abspath
from optparse import OptionParser
from okeanos_utils import *


# Definitions of return value errors
error_flavor_list = -23
error_user_quota = -22

# Global constants
REPORT = 25  # Define logging level of REPORT
Bytes_to_GB = 1073741824  # Global to convert bytes to gigabytes
Bytes_to_MB = 1048576  # Global to convert bytes to megabytes
auth_url='https://accounts.okeanos.grnet.gr/identity/v2.0'

def check_quota(token):
    '''
    Checks if user available quota .
    Available = limit minus (used and pending).Also divides with 1024*1024*1024
    to transform bytes to gigabytes.
     '''

    auth = check_credentials(token, auth_url)

    try:
        dict_quotas = auth.get_quotas()
    except Exception:
        logging.exception('Could not get user quota')
        sys.exit(error_user_quota)
    limit_cd = dict_quotas['system']['cyclades.disk']['limit'] / Bytes_to_GB
    usage_cd = dict_quotas['system']['cyclades.disk']['usage'] / Bytes_to_GB
    pending_cd = dict_quotas['system']['cyclades.disk']['pending'] / Bytes_to_GB
    available_cyclades_disk_GB = (limit_cd-usage_cd-pending_cd) 


    limit_cpu = dict_quotas['system']['cyclades.cpu']['limit']
    usage_cpu = dict_quotas['system']['cyclades.cpu']['usage']
    pending_cpu = dict_quotas['system']['cyclades.cpu']['pending']
    available_cpu = limit_cpu - usage_cpu - pending_cpu
    

    limit_ram = dict_quotas['system']['cyclades.ram']['limit'] / Bytes_to_MB  
    usage_ram = dict_quotas['system']['cyclades.ram']['usage'] / Bytes_to_MB
    pending_ram = dict_quotas['system']['cyclades.ram']['pending'] / Bytes_to_MB
    available_ram = (limit_ram-usage_ram-pending_ram)

    limit_vm = dict_quotas['system']['cyclades.vm']['limit']
    usage_vm = dict_quotas['system']['cyclades.vm']['usage']
    pending_vm = dict_quotas['system']['cyclades.vm']['pending']
    available_vm = limit_vm-usage_vm-pending_vm
    
    quotas = {'cpus' : { 'limit' : limit_cpu , 'available' : available_cpu } , 
              'ram' : {'limit' : limit_ram , 'available' : available_ram } , 
              'disk' : {'limit' : limit_cd , 'available' : available_cyclades_disk_GB } , 
              'cluster_size' : {'limit' : limit_vm , 'available' : available_vm }}
    logging.log(REPORT, quotas)
    return


def main(opts):
    '''
    The main function calls create_cluster with the arguments given from
    command line.
    '''
    check_quota(opts.token)

if __name__ == '__main__':

    #  Add some interaction candy

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    levels = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'report': REPORT,
              'info': logging.INFO,
              'debug': logging.DEBUG}

    # Create string with all available logging levels
    string_of_levels = ''
    for level_name in levels.keys():
        string_of_levels = string_of_levels + level_name + '|'
    string_of_levels = string_of_levels[:-1]

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')

    parser.add_option('--logging_level',
                      action='store', type='string', dest='logging_level',
                      metavar='LOGGING LEVEL',
                      help='logging level:[' +
                      string_of_levels +
                      ']. Default is report',
                      default='report')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    #  If clause to catch syntax error in logging argument
    if opts.logging_level not in levels.keys():
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

    if not opts.token:
        logging.error('invalid syntax for authentication token')
        sys.exit(error_syntax_auth_token)

    main(opts)

            
