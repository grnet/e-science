# -*- coding: utf-8 -*-

'''
Django backend to update the database after a new logout action

@author: Ioannis Stenos, Nick Vrionis
'''
import django
import os
import sys
import logging
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError
from app_escience.models import *
from django.core.exceptions import *
from authenticate_user import *
from django.utils import timezone
django.setup()

# Constants
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'

# Definitions of return value errors
error_multiple_entries = -1


def get_user_id(token):
    '''
    Check kamaki and returns user uuid from matching token
    '''
    auth = AstakosClient(auth_url, token)
    try:
        logging.info(' Get the uuid')
        uuid = auth.user_info['id']
        return db_after_logout(uuid)
    except ClientError:
        logging.error('Failed to get user_id from identity server')
        raise


def db_after_logout(given_uuid):
    '''
    Check if user already exits in DB or if 
    it is a new user,make a new entry in UserInfo
    Each user must be only once in the UserInfo 
    if there are multiple entries raise an error
    '''
    try:
        existing_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the user %s is %d', existing_user.uuid,
                    existing_user.user_id)
        # user already in db
        db_logout_entry(existing_user)
        return existing_user

    except ObjectDoesNotExist:
        # new user 
        logging.warning(' Logout functionality only for existing users not new ones ')
        return 
    except MultipleObjectsReturned:
        # Problem with database table
        logging.error(' Table has multiple entries for the same uuid')

def db_logout_entry(user):
    '''
    Makes a new entry in the UserLogin
    table when the user logs out 
    '''  
    current_date = timezone.now()
    new_logout = UserLogin(user_id = user , action_date = current_date , login_status = "1")
    new_logout.save()
    return


