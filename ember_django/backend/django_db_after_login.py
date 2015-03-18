#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django script to update the database after a new login, logout,
create, or destroy cluster action.

@author: Ioannis Stenos, Nick Vrionis
"""

import django
import logging
from kamaki.clients.astakos import AstakosClient, CachedAstakosClient
from kamaki.clients import ClientError
from backend.models import *
from django.core.exceptions import *
from authenticate_user import *
from django.utils import timezone
from cluster_errors_constants import *
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

def get_user_name(token):
    """Check kamaki and return user name / email from matching ~okeanos token"""
    cached = CachedAstakosClient(auth_url, token)
    uuid = get_user_id(token)
    try:
        logging.info(' Get the user_name')
        user_name = cached.uuids2usernames((uuid,), token).get(uuid,'')
        return user_name
    except ClientError:
        msg = 'Failed to get user_name from identity server'
        raise ClientError(msg)

def db_after_login(token, login=True):
    """
    Check if a user already exists in DB or make a new entry in UserInfo
    if it is a new user. Each user must have one entry in the UserInfo.
    If there are multiple entries, then raise an error.
    Also checks if okeanos token has changed and updates it in db.
    """
    given_uuid = get_user_id(token)
    cached_user_name = get_user_name(token)
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
        if existing_user.user_name != cached_user_name:
            existing_user.user_name = cached_user_name
            existing_user.save()
        return existing_user

    except ObjectDoesNotExist:
        # new user database entry
        new_entry = UserInfo.objects.create(uuid=given_uuid, okeanos_token=token, user_name=cached_user_name)
        new_token = Token.objects.create(user=new_entry)
        new_user = UserInfo.objects.get(uuid=given_uuid)
        logging.info(' The id of the new user is '+ str(new_user.user_id))
        if login:
            db_login_entry(new_user)
        return new_user
    except MultipleObjectsReturned:
        # Problem with database table
        msg = ' Table has multiple entries for the same uuid'
        raise MultipleObjectsReturned(msg, error_multiple_entries)


def db_cluster_create(choices, task_id):
    """Updates DB after user request for cluster creation"""
    user =  UserInfo.objects.get(okeanos_token=choices['token'])
    new_cluster = ClusterInfo.objects.create(cluster_name=choices['cluster_name'], action_date=timezone.now(),
                    cluster_status=const_cluster_status_pending, cluster_size=choices['cluster_size'],
                    cpu_master=choices['cpu_master'],
                    ram_master=choices['ram_master'],
                    disk_master=choices['disk_master'],
                    cpu_slaves=choices['cpu_slaves'],
                    ram_slaves=choices['ram_slaves'],
                    disk_slaves=choices['disk_slaves'],
                    disk_template=choices['disk_template'],
                    os_image=choices['os_choice'], user_id=user,
                    project_name=choices['project_name'],
                    task_id=task_id,
                    state='Authenticated',
                    hadoop_status=const_hadoop_status_stopped)

    return new_cluster.id

def db_hadoop_update(cluster_id, hadoop_status, state):
    try:
        cluster = ClusterInfo.objects.get(id=cluster_id)
    except ObjectDoesNotExist:
        msg = 'Cluster with given id does not exist'
        raise ObjectDoesNotExist(msg)

    cluster.state = state
    if hadoop_status == 'Pending':
        cluster.hadoop_status = const_hadoop_status_pending
    else:
        cluster.hadoop_status =  HADOOP_STATUS_ACTIONS[hadoop_status][0]
    cluster.save()
        

def db_cluster_update(token, status, cluster_id, master_IP='', state='', password=''):
    """
    Updates DB when cluster is created or deleted from pending status and
    when cluster state changes.
    """
    try:
        user = UserInfo.objects.get(okeanos_token=token)
        cluster = ClusterInfo.objects.get(id=cluster_id)
    except ObjectDoesNotExist:
        msg = 'Cluster with given name does not exist in pending state'
        raise ObjectDoesNotExist(msg)
    if password:
        user.master_vm_password = u'The root password of \"{0}\"({1}) master VM is {2}'.format(cluster.cluster_name,cluster.id,password)

    if status == "Active":
        cluster.cluster_status = const_cluster_status_active
        user.master_vm_password = ''

    if status == "Pending":
        cluster.cluster_status = const_cluster_status_pending

    elif status == "Destroyed":
        cluster.cluster_status = const_cluster_status_destroyed
        cluster.master_IP = ''
        cluster.state= 'Deleted'
        cluster.hadoop_status = const_hadoop_status_stopped

    if state:
        cluster.state = state
    if master_IP:
        cluster.master_IP = master_IP
    user.save()
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
