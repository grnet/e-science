#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django script to update the database after a new login, logout,
create, or destroy cluster action.

@author: Ioannis Stenos, Nick Vrionis
"""

import django
import logging
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError
from backend.models import *
from django.core.exceptions import *
from authenticate_user import *
from django.utils import timezone
from orka.cluster_errors_constants import *
django.setup()


def get_user_id(token):
    """Check kamaki and returns user uuid from matching ~okeanos token"""
    auth = AstakosClient(auth_url, token)
    try:
        logging.info(' Get the uuid')
        uuid = auth.user_info['id']
        return uuid
    except ClientError:
        msg = 'Failed to get uuid from identity server'
        raise ClientError(msg)


def db_after_login(token, login=True):
    """
    Check if a user already exists in DB or make a new entry in UserInfo
    if it is a new user. Each user must have one entry in the UserInfo.
    If there are multiple entries, then raise an error.
    Also checks if okeanos token has changed and updates it in db.
    """
    given_uuid = get_user_id(token)
    try:
        existing_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the user %s is %d', existing_user.uuid,
                     existing_user.user_id)
        # user already in db
        if login:
            db_login_entry(existing_user)
        if existing_user.okeanos_token != token:
            existing_user.okeanos_token = token
            existing_user.save()
        return existing_user

    except ObjectDoesNotExist:
        # new user database entry
        new_entry = UserInfo(uuid=given_uuid, okeanos_token=token)
        new_entry.save()
        new_token = Token(user=new_entry)
        new_token.save()
        new_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the new user is '+ str(new_user.user_id))
        if login:
            db_login_entry(new_user)
        return new_user
    except MultipleObjectsReturned:
        # Problem with database table
        msg = ' Table has multiple entries for the same uuid'
        raise MultipleObjectsReturned(msg, error_multiple_entries)


def db_cluster_create(user, choices):
    """Updates DB after user request for cluster creation"""
    ClusterInfo(cluster_name=choices['cluster_name'], action_date=timezone.now(),
                cluster_status="2", cluster_size=choices['cluster_size'],
                cpu_master=choices['cpu_master'],
                mem_master=choices['mem_master'],
                disk_master=choices['disk_master'],
                cpu_slaves=choices['cpu_slaves'],
                mem_slaves=choices['mem_slaves'],
                disk_slaves=choices['disk_slaves'],
                disk_template=choices['disk_template'],
                os_image=choices['os_choice'], user_id=user,
                project_name=choices['project_name'],
                task_id=choices['task_id'],
                state='AUTHENTICATED').save()


def db_cluster_update(user, status, cluster_name, master_IP='', state=''):
    """Updates DB when cluster is created or deleted from pending state"""
    try:
        cluster = ClusterInfo.objects.get(user_id=user, cluster_name=cluster_name)
    except ObjectDoesNotExist:
        msg = 'Cluster with given name does not exist in pending state'
        raise ObjectDoesNotExist(msg)

    if status == "Active":
        cluster.cluster_status = "1"

    if status == "Pending":
        cluster.cluster_status = "2"

    elif status == "Destroyed":
        cluster.cluster_status = "0"
        cluster.master_IP = ''
        cluster.state= 'Deleted'

    if state:
        cluster.state = state
    if master_IP:
        cluster.master_IP = master_IP
    cluster.save()


def db_login_entry(user):
    """
    Makes a new entry in the UserLogin
    table when the user logs in
    """
    current_date = timezone.now()
    new_login = UserLogin(user_id=user, action_date=current_date,
                          login_status="0")
    new_login.save()
    return


def db_logout_entry(user):
    """
    Makes a new entry in the UserLogin
    table when the user logs out
    """
    current_date = timezone.now()
    new_logout = UserLogin(user_id=user, action_date=current_date,
                           login_status="1")
    new_logout.save()
    return
