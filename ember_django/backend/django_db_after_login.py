#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Django script to update the database after a new login or logout action

@author: Ioannis Stenos, Nick Vrionis
'''

import django
import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError
from backend.models import *
from django.core.exceptions import *
from authenticate_user import *
from django.utils import timezone
django.setup()

# Constants
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'

# Definitions of return value errors
error_multiple_entries = -1


def get_user_id(token):
    '''Check kamaki and returns user uuid from matching ~okeanos token'''
    auth = AstakosClient(auth_url, token)
    try:
        logging.info(' Get the uuid')
        uuid = auth.user_info['id']
        return db_after_login(uuid)
    except ClientError:
        logging.error('Failed to get uuid from identity server')
        raise


def db_after_login(given_uuid):
    '''
    Check if a user already exists in DB or make a new entry in UserInfo
    if it is a new user. Each user must have one entry in the UserInfo.
    If there are multiple entries, then raise an error.
    '''
    try:
        existing_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the user %s is %d', existing_user.uuid,
                     existing_user.user_id)
        # user already in db
        db_login_entry(existing_user)
        return existing_user

    except ObjectDoesNotExist:
        # new user database entry
        new_entry = UserInfo(uuid=given_uuid)
        new_entry.save()
        new_token = Token(user=new_entry)
        new_token.save()
        new_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the new user is ', new_user.user_id)
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
    current_date = timezone.now()
    new_login = UserLogin(user_id=user, action_date=current_date,
                          login_status="0")
    new_login.save()
    return


def db_logout_entry(user):
    '''
    Makes a new entry in the UserLogin
    table when the user logs out
    '''
    current_date = timezone.now()
    new_logout = UserLogin(user_id=user, action_date=current_date,
                           login_status="1")
    new_logout.save()
    return
