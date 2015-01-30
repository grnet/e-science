#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from os.path import abspath, dirname, join
from cluster_errors_constants import *
from kamaki.clients import ClientError
from ConfigParser import RawConfigParser, NoSectionError
import requests
import json
from collections import OrderedDict

def get_api_urls(action):
    """ Return api urls from config file"""
    parser = RawConfigParser()
    orka_dir = dirname(abspath(__file__))
    config_file = join(orka_dir, 'config.txt')
    parser.read(config_file)
    try:
        base_url = parser.get('Web', 'url')
        if action == 'login':
            url_login = '{0}{1}'.format(base_url, login_endpoint)
            return url_login
        if action == 'database':
            url_database = '{0}{1}'.format(base_url, database_endpoint)
            return url_database
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
        msg = 'Not a valid api url in config file'
        raise NoSectionError(msg)


class OrkaRequest(object):
    """Class for REST requests in orka database."""
    def __init__(self, escience_token, payload, action='database'):
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
        requests.delete(self.url, data=json.dumps(self.payload),
                        headers=self.headers)

    def retrieve(self):
        """Request to retrieve info from an endpoint."""
        r = requests.get(self.url, data=json.dumps(self.payload),
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
    orka_request = OrkaRequest(escience_token, payload, action='login')
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
    escience_token = response['user']['escience_token']
    logging.log(REPORT, ' Authenticated with escience database')
    return escience_token


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