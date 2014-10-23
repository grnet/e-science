#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This returns the flavors based on kamaki flavor list.

@author: Ioannis Stenos, Nick Vrionis
'''

import os
import logging
from sys import argv
from os.path import abspath
from optparse import OptionParser
from okeanos_utils import *
from kamaki.clients.cyclades import CycladesClient


# Definitions of return value errors
error_flavor_list = -23


# Global constants
REPORT = 25  # Define logging level of REPORT
auth_url='https://accounts.okeanos.grnet.gr/identity/v2.0'

def get_flavor_id(token):
    '''From kamaki flavor list get all possible flavors '''

    auth = check_credentials(token, auth_url)
    endpoints, user_id = endpoints_and_user_id(auth)
    cyclades = init_cyclades(endpoints['cyclades'], token)

    try:
        flavor_list = cyclades.list_flavors(True)
    except Exception:
        logging.exception('Could not get list of flavors')
        sys.exit(error_flavor_list)
    print 'Start'
    cpu_list = []
    ram_list = []
    disk_list = []
    disk_template_list = []
  #  print flavor_list[0]['ram']
    for flavor in flavor_list:
        if flavor['vcpus'] not in cpu_list:
            cpu_list.append(flavor['vcpus'])
        if flavor['ram'] not in ram_list:
            ram_list.append(flavor['ram'])
        if flavor['disk'] not in disk_list:
            disk_list.append(flavor['disk'])
        if flavor['SNF:disk_template'] not in disk_template_list:
            disk_template_list.append(flavor['SNF:disk_template'])
    cpu_list = sorted (cpu_list)
    ram_list = sorted(ram_list)
    disk_list = sorted(disk_list)
    flavors = {'cpus' : cpu_list, 'ram' : ram_list , 'disk' : disk_list , 'disk_template' : disk_template_list}
    logging.log(REPORT, flavors)
    return flavors
    




def main(opts):
    '''
    The main function calls create_cluster with the arguments given from
    command line.
    '''
    get_flavor_id(opts.token)

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

            
