# -*- coding: utf-8 -*-

'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''
import django
import os
import sys
import datetime
django.setup()
import logging
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError
from app_escience.models import *
from django.core.exceptions import *
from authenticate_user import *

# Constants
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
REPORT = 25

# Definitions of return value errors
error_multiple_entries = -1





def get_user_id(token):
    '''
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    '''
    auth = AstakosClient(auth_url, token)
    try:
        logging.info(' Get the uuid')
        uuid = auth.user_info['id']
        return db_after_login(uuid)
    except ClientError:
        logging.error('Failed to get user_id from identity server')
        raise



def db_after_login(given_uuid):
    '''
    Check if user already exits in DB or if 
    it is a new user,make anew entry in UserInfo
    Each user must be only oncee in the UserInfo 
    if there are multiple entires raise an error
    '''

    try:
        existing_user = UserInfo.objects.get(uuid=given_uuid)
        logging.log(REPORT, ' The id of the user %s is %d', existing_user.uuid,
                    existing_user.user_id)
        print 'test'
        # user already in db
        db_logout_entry(existing_user)
        return existing_user

    except ObjectDoesNotExist:
        # new user database entry
        new_entry = UserInfo(uuid=given_uuid)
        new_entry.save()
        new_user = UserInfo.objects.get(uuid=given_uuid)
        logging.log(REPORT, ' The id of the new user is ', new_user.user_id)
        db_login_entry(new_user)
        return new_user
    except MultipleObjectsReturned:
        # Problem with database table
        logging.error(' Table has multiple entries for the same uuid')
        sys.exit(error_multiple_entries)



def db_login_entry(user):
    '''
    Makes a new entry in the UserLogin
    table when the user logs in 
    '''
    current_date = datetime.datetime.now()
    new_login = UserLogin(user_id =user , action_date = current_date , login_status = "0")
    new_login.save()
    return


def db_logout_entry(user):
    '''
    Makes a new entry in the UserLogin
    table when the user logs out 
    '''  
    current_date = datetime.datetime.now()
    new_logout = UserLogin(user_id = user , action_date = current_date , login_status = "1")
    new_logout.save()
    return


def main():

    token = 'fhjcj'
    if check_credentials(token) == AUTHENTICATED:
        get_user_id(token)
    else:
        logging.error('Not Authorized!!! ')
    
if __name__ == '__main__':
    
    levels = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'report': REPORT,
              'info': logging.INFO,
              'debug': logging.DEBUG}
    
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger(__name__)

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')

    main()
