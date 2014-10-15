
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
import json
import os.path
import esciencedjango.settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.apend('~/e-science/esciencedjango/app_escience')
django.setup()
import logging
import nose
 
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
error_new_user_logout = -2


def test_db_login():
    '''
    test function to check the login functionlity of a user 
    expect to retun UserInfo and UserLogin with status 0
    '''
    f = open ('token_file' ,'r')
    token = f.readline()
    f.close()
    token = token.strip()
    if check_credentials(token) == AUTHENTICATED:
        get_user_id(token)
    else:
        logging.error('Not Authorized!!! ')

    uuid = get_user_id(token)
    user = db_after_login(uuid)
    report = db_login_entry(user)
    print json.loads(user) , json.loads(report)
    return user , report



def test_db_logout():
    '''
    test function to check the login functionlity of a user 
    expect to retun  UserLogin with status 1
    '''
    f = open ('token_file' ,'r')
    token = f.readline()
    f.close()
    if check_credentials(token) == AUTHENTICATED:
           get_user_id(token)
    else:
        logging.error('Not Authorized!!! ')

    uuid = get_user_id(token)
    user, old_user = db_after_login(uuid)
    if old_user:
        report = db_login_entry(user)
    else:
        logging.error('Can not logout new user')
        sys.exit(error_new_user_logout)
    print json.loads(report)
    return report



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
        return uuid
    except ClientError:
        logging.error('Failed to get user_id from identity server')
        raise




def db_after_login(given_uuid):

    '''
    Check if user already exists in DB or
    if  it is a new user make a new entry in the DB
    Each user must be only once in the UserInfo if there are multiple entries
    raise an error. 
    '''

    old_user = 0

    try:
        existing_user = UserInfo.objects.get(uuid=given_uuid)
        logging.log(REPORT, ' The id of the user %s is %d', existing_user.uuid,
                    existing_user.user_id)
        old_user = 1
        # user already in db
        return existing_user , old_user

    except ObjectDoesNotExist:
        # new user database entry
        new_entry = UserInfo(uuid=given_uuid)
        new_entry.save()
        new_user = UserInfo.objects.get(uuid=given_uuid)
        logging.log(REPORT, ' The id of the new user is ', new_user.user_id)
        return new_user
    except MultipleObjectsReturned:
        # Problem with database table
        logging.error(' Table has multiple entries for the same uuid')
        sys.exit(error_multiple_entries)



def db_login_entry(user):
    '''
    Makes a new entry in the UserLogin table 
    when the user logs in with the relevant 
    time.
    '''

    current_date = datetime.datetime.now()
    new_login = UserLogin(user_id =user , action_date = current_date , login_status = "0")
    new_login.save()
    return new_login


def db_logout_entry(user):
    '''
    When user logs out makes an new entry in UserLogin table
    with the time and the log out status 
    '''

    current_date = datetime.datetime.now()
    new_logout = UserLogin(user_id = user , action_date = current_date , login_status = "1")
    new_logout.save()
    return new_logout



def main():

    test_db_login()    
    
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