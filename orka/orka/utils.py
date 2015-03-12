#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from os.path import abspath, dirname, join, expanduser
from cluster_errors_constants import *
from kamaki.clients import ClientError
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
import requests
from requests import ConnectionError
import json
import re
from collections import OrderedDict
from operator import itemgetter, attrgetter, methodcaller
from datetime import datetime
import subprocess
import xml.etree.ElementTree as ET

def get_from_kamaki_conf(section, option, action=None):
    """ 
    Process option 'option' from section 'section' from .kamakirc file 
    applying optional 'action' to it and return it
    """
    parser = RawConfigParser()
    user_home = expanduser('~')
    config_file = join(user_home, ".kamakirc")
    parser.read(config_file)
    try:
        option_value = parser.get(section,option)
    except NoSectionError:
        msg = ' Could not find section \'{0}\' in .kamakirc'.format(section)
        raise ClientError(msg, error_syntax_auth_token)
    except NoOptionError:
        msg = ' Could not find option \'{0}\' in section \'{1}\' in .kamakirc'.format(option,section)
        raise ClientError(msg, error_syntax_auth_token)
    
    if option_value:
        if not action:
            return option_value
        else:
            if action == 'login':
                url_login = '{0}{1}'.format(option_value, login_endpoint)
                return url_login
            if action == 'cluster':
                url_cluster = '{0}{1}'.format(option_value, cluster_endpoint)
                return url_cluster
            if action == 'job':
                url_job = '{0}{1}'.format(option_value, job_endpoint)
                return url_job
            if action == 'hdfs':
                url_hdfs = '{0}{1}'.format(option_value, hdfs_endpoint)
                return url_hdfs
            else:
                logging.log(SUMMARY, ' Url to be returned from .kamakirc not specified')
                return 0


class ClusterRequest(object):
    """Class for REST requests to application server."""
    def __init__(self, escience_token, payload, action='login'):
        """
        Initialize escience token used for token authentication, payload
        and appropriate headers for the request.
        """
        self.escience_token = escience_token
        self.payload = payload
        self.url = get_from_kamaki_conf('orka','base_url',action)
        self.headers = {'Accept': 'application/json','content-type': 'application/json',
                        'Authorization': 'Token ' + self.escience_token}

    def create_cluster(self):
        """Request to create a Hadoop Cluster in ~okeanos."""
        r = requests.put(self.url, data=json.dumps(self.payload),
                         headers=self.headers)
        response = json.loads(r.text)
        return response

    def delete_cluster(self):
        """Request to delete a Hadoop Cluster in ~okeanos."""
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

    def post(self):
        """POST request to server"""
        r = requests.post(self.url, data=json.dumps(self.payload),
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
    try:
        url_login = get_from_kamaki_conf('orka','base_url',action='login')
    except ClientError, e:
        raise e
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
    If the passed-in datetime string can't be reformatted, return it unaltered
    strptime expects microseconds so we try to capture both with and w/o microsecond utc format 
    and right-pad the milisecond segment to microseconds.
    """
    datestring_microsec = datestring
    datestring_microsec = re.sub(':(\d+)Z$', lambda m: ':{0}.000000Z'.format(m.group(1)), datestring_microsec)
    datestring_microsec = re.sub('\.(\d+)Z$', lambda m: '.{:0<6}Z'.format(m.group(1)), datestring_microsec)
    date_formats = {'shortdate':'%Y-%m-%d', 'shortdatetime':'%a, %d %b %Y %H:%M:%S'}
    date_fmt = date_formats.has_key(fmt) and date_formats[fmt] or date_formats['shortdatetime']
    try:
        date_in = datetime.strptime(datestring_microsec, '%Y-%m-%dT%H:%M:%S.%fZ')
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

def custom_sort_list(input_list, keys, functions={}, getter=itemgetter):
    """
    Sort a list of dictionary objects or objects by multiple keys ascending/descending.
    Keyword Arguments:
    input_list -- A list of dictionary objects or objects
    keys -- A list of key names to sort by. Use -key to sort in descending order
    functions -- A Dictionary of Key Name -> Functions to process each key value
    getter -- Default "getter" if key function does not exist
              operator.itemgetter for Dictionaries
              operator.attrgetter for Objects
    Example:
            people = [{'name':'John', 'age':30},{'name':'Adam', 'age':33}]
            sorted_people = custom_sort_list(people,['name','-age'])
            print people
            print sorted_people
    """
    comparers = list()
    for key in keys:
        column = key[1:] if key.startswith('-') else key
        if not column in functions:
            functions[column] = getter(column)
        comparers.append((functions[column], 1 if column == key else -1))

    def comparer(left, right):
        for func, direction in comparers:
            result = cmp(func(left), func(right))
            if result:
                return direction * result
        else:
            return 0
    return sorted(input_list, cmp=comparer)

def compose(inner_func, *outer_funcs):
     """
     function factory: gets a list of unary functions and combines them in a single function
     Example: 
             people = [{'name':'John', 'age':30},{'name':'Adam', 'age':33}]
             get_name_upper = compose(itemgetter('name'), methodcaller('upper'))
             sorted_people = custom_sort_list(people, ['name'], {'name':get_name_upper})
     """
     if not outer_funcs:
         return inner_func
     outer_func = compose(*outer_funcs)
     return lambda *args, **kwargs: outer_func(inner_func(*args, **kwargs))

def ssh_call_hadoop(user, master_IP, func_arg):
    """
        SSH to master VM
        and make Hadoop calls
    """
    response = subprocess.call( "ssh " + user + "@" + master_IP + " \"" + HADOOP_PATH 
                     + func_arg + "\"", stderr=FNULL, shell=True)
    
    return response

def ssh_check_output_hadoop(user, master_IP, func_arg):
    """
        SSH to master VM
        and check output of Hadoop calls
    """
    response = subprocess.check_output( "ssh " + user + "@" + master_IP + " \"" + HADOOP_PATH 
                     + func_arg + "\"", stderr=FNULL, shell=True).splitlines()
    
    return response

def ssh_stream_to__hadoop(user, master_IP, source_file, dest_dir):
    """
        SSH to master VM
        and stream files to hadoop
    """
    response = subprocess.call("cat " + source_file
                                    + " | ssh " + user + "@" + master_IP 
                                    + " " + HADOOP_PATH + " dfs -put - " + dest_dir, stderr=FNULL, shell=True)

    return response

def read_replication_factor(user, master_IP):
    """
        SSH to master VM
        and read the replication factor
        from the hdfs-site.xml 
    """
    hdfs_xml = subprocess.check_output("ssh " + user + "@" + master_IP 
                                            + " \"" + "cat /usr/local/hadoop/etc/hadoop/hdfs-site.xml\"", 
                                            shell=True)

    doc = ET.ElementTree(ET.fromstring(hdfs_xml))
    root = doc.getroot()
    for child in root.iter("property"):
        name = child.find("name").text
        if name == "dfs.replication":
            replication_factor = int(child.find("value").text)
            break

    return replication_factor

def ssh_stream_from__hadoop(user, master_IP, source_file, dest_dir, filename):
    """
        SSH to master VM and
        stream files from hadoop to local
    """
    response = subprocess.call("ssh " + user + "@"
                                    + master_IP + " \"" + HADOOP_PATH
                                    + " dfs -text " + source_file + "\""
                                    + " | tee 1>>" + dest_dir + "/" + filename, stderr=FNULL, shell=True)
    
    return response

def parse_hdfs_dest(regex, path):
    """
    Parses remote hdfs directory for the orka put command to check if directory exists.
    """
    parsed_path = re.match(regex, path)
    if parsed_path:
        return parsed_path.group(1)
    else:
        return parsed_path