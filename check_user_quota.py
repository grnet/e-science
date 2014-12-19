'''
This script checks user's quota (and returns them)
'''

from optparse import OptionParser
from sys import argv, exit
import logging
import os, sys
from os.path import join, dirname, abspath

sys.path.append(join(dirname(abspath(__file__)), 'ember_django/backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
from okeanos_utils import check_quota, get_project_id
from cluster_errors_constants import *

def main(opts):
    '''
    The main function calls the check_quota 
    with auth token and project id
    '''
    project_id=get_project_id(opts.token, opts.project_name)
    quotas = check_quota(opts.token, project_id)

    print quotas
    
    
if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deletes a cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--project_name',
                      action='store', type='string', dest='project_name',
                      metavar="PROJECT_NAME",
                      help='The name of the project')
    parser.add_option('--token',
                      action='store', type='string', dest='token',
                      metavar='AUTH TOKEN',
                      help='Synnefo authentication token')

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')

    if not opts.project_name:
        logging.error('invalid syntax for project name')
        exit(error_proj_id)

    if not opts.token:
        logging.error('invalid syntax for authentication token')
        exit(error_syntax_token)
    main(opts)