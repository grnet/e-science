#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from os.path import abspath, dirname, join, expanduser
from cluster_errors_constants import *
from kamaki.clients import ClientError
from ConfigParser import RawConfigParser, NoSectionError
import requests
from requests import ConnectionError
import json
from collections import OrderedDict
from datetime import datetime

def get_api_urls(action):
    """ Return api urls from config file"""
    parser = RawConfigParser()
    user_home = expanduser('~')
    config_file = join(user_home, ".kamakirc")
    parser.read(config_file)
    try:
        base_url = parser.get('orka', 'base_url')
        if action == 'login':
            url_login = '{0}{1}'.format(base_url, login_endpoint)
            return url_login
        if action == 'cluster':
            url_cluster = '{0}{1}'.format(base_url, cluster_endpoint)
            return url_cluster
        if action == 'job':
            url_job = '{0}{1}'.format(base_url, job_endpoint)
            return url_job
        else:
            logging.log(SUMMARY, ' Url to be returned from config file not specified')
            return 0
    except NoSectionError:
        msg = 'Did not find a valid orka api base_url in .kamakirc'
        raise NoSectionError(msg)


class ClusterRequest(object):
    """Class for REST requests in orka database."""
    def __init__(self, escience_token, payload, action='login'):
        """
        Initialize escience token used for token authentication, payload
        and appropriate headers for the request.
        """
        self.escience_token = escience_token
        self.payload = payload
        self.url = get_api_urls(action)
        self.headers = {'Accept': 'application/json','content-type': 'application/json',
                        'Authorization': 'Token ' + self.escience_token}

    def create_cluster(self):
        """
        Request to orka database that cluster creation is
        starting (pending status update)
        """
        r = requests.put(self.url, data=json.dumps(self.payload),
                         headers=self.headers)
        response = json.loads(r.text)
        return response

    def delete_cluster(self):
        """
        Request to orka database for cluster deleting from CLI
        (Destroyed status update)"""
        r = requests.delete(self.url, data=json.dumps(self.payload),
                            headers=self.headers)
        response = json.loads(r.text)
        return response

    def retrieve(self):
        """Request to retrieve info from an endpoint."""
        r = requests.get(self.url, data=json.dumps(self.payload),
                         headers=self.headers)
        response = json.loads(r.text)
        return response
    
    def update_hadoop_status(self):
        r = requests.put('http://127.0.0.1:8000/api/hadoopchoices', data=json.dumps(self.payload),
                         headers=self.headers)
        response = json.loads(r.text)
        return response
        


def get_user_clusters(token):
    """
    Get the clusters of the user
    """
    try:
        escience_token = authenticate_escience(token)
    except TypeError:
        msg = ' Authentication error with token: ' + token
        raise ClientError(msg, error_authentication)
    except Exception,e:
        print ' ' + str(e.args[0])

    payload = {"user": {"id": 1}}
    orka_request = ClusterRequest(escience_token, payload, action='login')
    user_data = orka_request.retrieve()
    user_clusters = user_data['user']['clusters']
    return user_clusters


def authenticate_escience(token):
    """
    Authenticate with escience database and retrieve escience token
    for Token Authentication
    """
    payload = {"user": {"token": token}}
    headers = {'content-type': 'application/json'}
    url_login = get_api_urls(action='login')
    r = requests.post(url_login, data=json.dumps(payload), headers=headers)
    response = json.loads(r.text)
    try:
        escience_token = response['user']['escience_token']
    except TypeError:
        msg = ' Authentication error with token: ' + token
        raise ClientError(msg, error_authentication)
    logging.log(REPORT, ' Authenticated with escience database')
    return escience_token


def custom_date_format(datestring, fmt='shortdatetime'):
    """
    Format a utc date time to human friendly date time.
    Both input and output are string representations of datetime
    If the passed in datetime string representation can't be reformatted it is returned unaltered
    """
    date_formats = {'shortdate':'%Y-%m-%d', 'shortdatetime':'%a %b %Y %H:%M:%S'}
    date_fmt = date_formats.has_key(fmt) and date_formats[fmt] or date_formats['shortdatetime']
    try:
        date_in = datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S.%fZ')
        return date_in.strftime(date_fmt)
    except ValueError:
        return datestring
    

def custom_sort_factory(order_list):
    """
    function factory: gets a list of lists with order keys
    and returns a function that will produce an OrderedDict
    with the specified order.
    Keys not present in the sort list are returned at the end.
    Example:
        fruits = {'apple': 'red', 'orange': 'orange', 'lemon': 'yellow', 'banana': 'yellow'}
        order_list = [['lemon','orange','banana','apple']]
        sort_function = custom_sort_factory(order_list)
        sorted_fruits = sort_function(fruits)
        print fruits
        print sorted_fruits
    """
    order_list = [{k: -i for (i, k) in enumerate(reversed(order), 1)} for order in order_list]
    def sorter(stuff):
        if isinstance(stuff, dict):
            l = [(k, sorter(v)) for (k, v) in stuff.iteritems()]
            keys = set(stuff)
            for order in order_list:
                if keys.issuperset(order):
                    return OrderedDict(sorted(l, key=lambda x: order.get(x[0], 0)))
            return OrderedDict(sorted(l))
        if isinstance(stuff, list):
            return [sorter(x) for x in stuff]
        return stuff
    return sorter