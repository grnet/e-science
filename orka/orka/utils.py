#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from cluster_errors_constants import *
from os.path import abspath, dirname, join, expanduser, isfile
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.image import ImageClient
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
from requests import ConnectionError
from collections import OrderedDict
from operator import itemgetter, attrgetter, methodcaller
from datetime import datetime
from subprocess import PIPE
from pipes import quote
import warnings
warnings.filterwarnings("ignore")


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
        raise NoSectionError(msg, error_syntax_auth_token)
    except NoOptionError:
        msg = ' Could not find option \'{0}\' in section \'{1}\' in .kamakirc'.format(option,section)
        raise NoOptionError(msg, error_syntax_auth_token)
    
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
            if action == 'vre':
                url_vre = '{0}{1}'.format(option_value, vre_endpoint)
                return url_vre
            if action == 'vre_images':
                url_vre_images = '{0}{1}'.format(option_value, vre_images_endpoint)
                return url_vre_images
            if action == 'orka_images':
                url_orka_images = '{0}{1}'.format(option_value, orka_images_endpoint)
                return url_orka_images
            if action == 'node':
                url_node = '{0}{1}'.format(option_value, cluster_endpoint)
                return url_node
            else:
                logging.log(SUMMARY, ' Url to be returned from .kamakirc not specified')
                return 0


class ClusterRequest(object):
    """Class for REST requests to application server."""
    def __init__(self, escience_token, server_url, payload, action='login'):
        """
        Initialize escience token used for token authentication, payload
        and appropriate headers for the request.
        """
        self.escience_token = escience_token
        self.payload = payload
        self.url = get_from_kamaki_conf('orka','base_url',action)
        self.url = server_url + re.split('https://[^/]+',self.url)[-1]
        try:
            ssl_property = get_from_kamaki_conf('orka','verify_ssl')
            self.VERIFY_SSL = validate_ssl_property(ssl_property)
        except (NoOptionError, IOError, TypeError):
            self.VERIFY_SSL = DEFAULT_SSL_VALUE
        self.headers = {'Accept': 'application/json','content-type': 'application/json'}
        
        if self.escience_token:
            self.headers.update({'Authorization': 'Token ' + self.escience_token})

    def create_cluster(self):
        """Request to create a Hadoop Cluster in ~okeanos."""
        r = requests.put(self.url, data=json.dumps(self.payload),
                         headers=self.headers, verify=self.VERIFY_SSL)
        response = json.loads(r.text)
        return response

    def delete_cluster(self):
        """Request to delete a Hadoop Cluster in ~okeanos."""
        r = requests.delete(self.url, data=json.dumps(self.payload),
                            headers=self.headers, verify=self.VERIFY_SSL)
        response = json.loads(r.text)
        return response

    def retrieve(self):
        """Request to retrieve info from an endpoint."""
        r = requests.get(self.url, data=json.dumps(self.payload),
                         headers=self.headers, verify=self.VERIFY_SSL)
        response = json.loads(r.text)
        return response

    def post(self):
        """POST request to server"""
        r = requests.post(self.url, data=json.dumps(self.payload),
                         headers=self.headers, verify=self.VERIFY_SSL)
        response = json.loads(r.text)
        return response


def get_user_clusters(token, server_url, choice='clusters'):
    """
    Get by default the clusters of the user. If choice argument is different
    e.g vreservers, returns info of user's VRE servers.
    """
    try:
        escience_token = authenticate_escience(token, server_url)
    except TypeError:
        msg = ' Authentication error: Invalid Token'
        raise ClientError(msg, error_authentication)
    except Exception, e:
        print ' ' + str(e.args[0])

    payload = {"user": {"id": 1}}
    orka_request = ClusterRequest(escience_token, server_url, payload, action='login')
    user_data = orka_request.retrieve()
    user_clusters = user_data['user']['{0}'.format(choice)]
    return user_clusters


def validate_ssl_property(ssl_property):
    """
    Validate ssl_property from kamakirc configuration file.
    """
    # Check if ssl_property is set to false or no.
    regex = re.compile(r"\bno\b|\bfalse\b", re.I)
    if regex.match(ssl_property):
        return False
    # Check if SSL certificate exists.
    if isfile(ssl_property):
        return ssl_property
    else:
        raise IOError('SSL certificate not found')


def authenticate_escience(token, server_url):
    """
    Authenticate with escience database and retrieve escience token
    for Token Authentication
    """
    payload = {"user": {"token": token}}
    headers = {'content-type': 'application/json'}
    try:
        ssl_property = get_from_kamaki_conf('orka','verify_ssl')
        VERIFY_SSL = validate_ssl_property(ssl_property)
    except (NoOptionError, IOError, TypeError):
        #print 'SSL certificate not found or verify_ssl property is not set in .kamakirc. SSL Verification disabled.'
        VERIFY_SSL = DEFAULT_SSL_VALUE
    try:
        url_login = server_url + login_endpoint
    except ClientError, e:
        raise e
    r = requests.post(url_login, data=json.dumps(payload), headers=headers, verify=VERIFY_SSL)
    response = json.loads(r.text)
    try:
        escience_token = response['user']['escience_token']
    except TypeError:
        msg = ' Authentication error: Invalid Token'
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


def ssh_call_hadoop(user, master_IP, func_arg, hadoop_path=HADOOP_PATH):
    """
        SSH to master VM
        and make Hadoop calls
    """
    response = subprocess.call( "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + user + "@" + master_IP + " \'" + hadoop_path
                     + func_arg + "\'", stderr=FNULL, shell=True)
    
    return response


def ssh_check_output_hadoop(user, master_IP, func_arg, hadoop_path=HADOOP_PATH):
    """
        SSH to master VM
        and check output of Hadoop calls
    """
    response = subprocess.check_output( "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + user + "@" + master_IP + " \'" + hadoop_path
                     + func_arg + "\'", stderr=FNULL, shell=True).splitlines()
    
    return response


def ssh_stream_to_hadoop(user, master_IP, source_file, dest_dir, hadoop_path=HADOOP_PATH):
    """
        SSH to master VM
        and stream files to hadoop
    """
    str_command = "cat " + "\"{0}\"".format(source_file) \
    + " | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " \
    + "{0}@{1} ".format(user,master_IP) \
    + "\"" + hadoop_path + " dfs -put - " + "\'{0}\'".format(dest_dir) + "\""
    
    response = subprocess.call(str_command, stderr=FNULL, shell=True)

    return response


def ssh_pithos_stream_to_hadoop(user, master_IP, source_file, dest_dir, pub=True):
    """
        SSH to master VM
        and stream files to hadoop
    """
    # keep this around for when we have streaming from kamaki
#     str_command = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " \
#     + "{0}@{1} ".format(user,master_IP) \
#     + "\'kamaki file cat " + "\"{0}\"".format(source_file) \
#     + " | " + "{0}".format(HADOOP_PATH) \
#     + " dfs -put - " + "\"{0}\"".format(dest_dir) + "\'"
#     response = subprocess.call(str_command, stderr=FNULL, shell=True)
#     return response
    
    # until then let's piggyback on put from server > hadoop streaming
    if pub==False:
        str_command = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + \
        "{0}@{1} ".format(user, master_IP) + \
        "\"kamaki file unpublish \'{0}\'\"".format(source_file)
        response = subprocess.call(str_command, stderr=FNULL, stdout=FNULL, shell=True)
        return response
    
    str_command = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + \
    "{0}@{1} ".format(user,master_IP) + \
    "\"kamaki file publish \'{0}\'\"".format(source_file)
    str_link = subprocess.check_output(str_command, stderr=FNULL, shell=True)
    remote_regex = re.compile("(?iu)((?:^ht|^f)+?tps?://)(.+)")
    result = remote_regex.match(str_link)
    if result:
        return result.group(0)
    else:
        return None
    

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


def ssh_stream_from_hadoop(user, master_IP, source_file, dest_dir):
    """
        SSH to master VM and
        stream files from hadoop to local
    """
    str_command = "ssh {0}@{1} ".format(user, master_IP) + \
    "\"{0} dfs -text ".format(HADOOP_PATH) + \
    "\'{0}\'\"".format(source_file) + \
    " > \'{0}\'".format(dest_dir)
    response = subprocess.call(str_command, stderr=FNULL, shell=True)

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


def get_file_protocol(filespec, fileaction="fileput", direction="source"):
    """ 
    Method to determine the file protocol (http/ftp, file, pithos etc)
    :input filespec, ['fileput|fileget|filemkdir'], ['source'|'destination']
    :output 'http-ftp|pithos|file|hdfs|unknown', ['path_without_protocol']
    """
    if fileaction == "fileput": # put <source> file to Hadoop FS.
        if direction == "source":
            # matches http:// https:// ftp:// ftps://
            remote_regex = re.compile("(?iu)((?:^ht|^f)+?tps?://)(.+)")
            # matches pithos://
            pithos_regex = re.compile("(?iu)((?:^pithos)+?:/)(.+)")
            # reject filespecs with a trailing slash /, still needs to be checked with os.path
            local_regex = re.compile("(?iu)(.+)(?<!/)$")
            result = remote_regex.match(filespec)
            if result:
                return "http-ftp", result.group(2)
            result = pithos_regex.match(filespec)
            if result:
                return "pithos", result.group(2)
            result = local_regex.match(filespec)
            if result:
                return "file", result.group(0)
            return "unknown", None
        elif direction == "destination":
            return "unknown", None
    elif fileaction == "fileget": # get <source> file from Hadoop FS to <destination> FS
        if direction == "destination":
            pithos_regex = re.compile("(?iu)((?:^pithos)+?://)(.+)")
            result = pithos_regex.match(filespec)
            if result:
                return "pithos", result.group(2)
            local_file_regex = re.compile("(?iu)(.+)(?<!/)$")
            result = local_file_regex.match(filespec)
            if result:
                return "file", result.group(0)
            local_folder_regex = re.compile("(?iu)(^/{1}[^/].+[^/]/{1}$)")
            result = local_folder_regex.match(filespec)
            if result:
                return "folder", result.group(0)
            return "unknown", None
        elif direction=="source":
            return "unknown", None
    elif fileaction == "filemkdir": # create directory on Hadoop FS
        if direction == "destination":
            # detect the existence of either of these patterns: //  \\ :// which would make this an invalid hdfs filespec
            bad_hdfs_regex = re.compile("(?iu)(.*)((?://)+|(?:\\\\)+|(?:\://?)+)(.*)")
            result = bad_hdfs_regex.match(filespec)
            if result:
                return "unknown", None
            else:
                return "hdfs", filespec
        elif direction=="source":
            return "unknown", None


def bytes_to_shorthand(num_bytes):
    """ 
    Method to Convert bytes to higher denominations.
    Support for all binary prefixes according to ISO-80000-13
    https://en.wikipedia.org/wiki/Binary_prefix
    :input int num_bytes
    :output str 'num_out suffix'
    """
    factor_to_suffix = [
                        (1024 ** 8, 'YiB'), # yotta ....
                        (1024 ** 7, 'ZiB'), # zetta ....
                        (1024 ** 6, 'EiB'), # exa   ....
                        (1024 ** 5, 'PiB'), # peta  ....
                        (1024 ** 4, 'TiB'), # tera  ....
                        (1024 ** 3, 'GiB'), # giga  ....
                        (1024 ** 2, 'MiB'), # mega  ....
                        (1024 ** 1, 'KiB'), # kilo  ....
                        (1024 ** 0, 'B'),   # ....  bytes
                        ]
    for factor, suffix in factor_to_suffix:
        if num_bytes >= factor:
            break
    
    if num_bytes%factor != 0:
        num_out = num_bytes/float(factor)
    else:
        num_out = num_bytes/factor
    
    if isinstance(num_out, (int,long,)):
        return "{:d}{:s}".format(num_out, suffix)
    elif isinstance(num_out, float):
        return "{:.2f}{:s}".format(num_out, suffix)
    else:
        return "{0}{1}".format(num_out, suffix)
 

def from_hdfs_to_pithos(user, master_IP, hdfs_path, dest_path):
    """
        SSH to master VM and 
        stream file from hdfs to pithos block by block
    """
    str_command = "ssh {0}@{1} ".format(user,master_IP) + \
    "\"kamaki container list --output-format json\""
    containers = subprocess.check_output(str_command, shell=True)
    list_of_pithos_containers = json.loads(containers)  
    container_exists = False
    if dest_path[0] == "/":
        container_name = dest_path.split('/')[1]
    else:
        container_name = 'pithos'
    for item in list_of_pithos_containers:
        if item["name"] == container_name:  # check if container exists in pithos
            container_exists = True
            container_project = item["x_container_policy"]["project"]
    if not container_exists:
        return -1
    str_command = "ssh {0}@{1} ".format(user,master_IP) + \
    "\"kamaki quota list --project-id {0} --output-format json --resource pithos.diskspace\"".format(container_project)
    quota = subprocess.check_output(str_command, shell=True)
    container_quota_list =json.loads(quota)
    str_command = "ssh {0}@{1} ".format(user,master_IP) + \
    "\"{0}".format(HADOOP_PATH) + " dfs -du \'{0}\'\"".format(hdfs_path)
    size_of_file = subprocess.check_output(str_command, shell=True).split()[0]
    file_size = int(size_of_file)   
    limit_pithos = container_quota_list[container_project]['pithos.diskspace']['limit']
    usage_pithos = container_quota_list[container_project]['pithos.diskspace']['usage']
    project_limit_pithos = container_quota_list[container_project]['pithos.diskspace']['project_limit']
    project_usage_pithos = container_quota_list[container_project]['pithos.diskspace']['project_usage']
    available_pithos = limit_pithos-usage_pithos
    if (available_pithos > (project_limit_pithos - project_usage_pithos)):
        available_pithos = project_limit_pithos - project_usage_vmpithos
    if file_size > available_pithos: # check pithos quota for file upload
        return -2
    str_command = "ssh {0}@{1} ".format(user,master_IP) + \
    "\"kamaki file create \'{0}\'\"".format(dest_path)
    
    subprocess.call(str_command, shell=True)   
    if file_size < block_size:
        str_command = "ssh {0}@{1} ".format(user,master_IP) + \
        "\"{0} dfs -get ".format(HADOOP_PATH) + \
        "\'{0}\' temp_file\"".format(hdfs_path)
        
        response_save_temp_file_1 = subprocess.call(str_command, shell=True )
        response_append_to_pithos_1 = subprocess.call("ssh " + user + "@"
                                    + master_IP +" kamaki file append temp_file " + dest_path , shell=True)
    else:
        file_left = file_size % block_size
        counter = 0
        str_command = "ssh {0}@{1} ".format(user,master_IP) + \
        "\"{0} dfs -cat ".format(HADOOP_PATH) + \
        "\'{0}\' ".format(hdfs_path) + \
        "| dd bs=1 skip=\'{0}\' ".format(counter * block_size) + \
        "count=\'{0}\' ".format(block_size) + \
        "> temp_file\""
                
        response_save_temp_file_2 = subprocess.call(str_command, shell=True )
        str_command = "ssh {0}@{1} ".format(user,master_IP) + \
        "\"kamaki file append temp_file \'{0}\'\"".format(dest_path)
        
        response_append_to_pithos_2 = subprocess.call(str_command, shell=True)
        counter +=1 
        while ((counter+1) * block_size) < file_size :
            str_command = "ssh {0}@{1} ".format(user,master_IP) + \
            "\"{0} dfs -cat ".format(HADOOP_PATH) + \
            "\'{0}\' ".format(hdfs_path) + \
            "| dd bs=\'{0}\' skip=1 iflag=fullblock ".format(counter * block_size) + \
            "| dd bs=\'{0}\' count=\'1\' > temp_file\"".format(block_size)
            
            response_save_temp_file_3 = subprocess.call(str_command, shell=True )
            str_command = "ssh {0}@{1} ".format(user,master_IP) + \
            "\"kamaki file append temp_file \'{0}\'\"".format(dest_path)
            
            response_append_to_pithos_3 = subprocess.call(str_command, shell=True)
            counter +=1 
        if file_left !=0:
            str_command = "ssh {0}@{1} ".format(user,master_IP) + \
            "\"{0} ".format(HADOOP_PATH) + \
            "dfs -cat \'{0}\' ".format(hdfs_path) + \
            "| dd bs=1 skip=\'{0}\' ".format(counter * block_size) + \
            "count=\'{0}\' ".format(file_left) + \
            "> temp_file\""
            
            response_save_temp_file_4 = subprocess.call(str_command, shell=True )
            str_command = "ssh {0}@{1} ".format(user,master_IP) + \
            "\"kamaki file append temp_file \'{0}\'\"".format(dest_path)
            
            response_append_to_pithos_4 = subprocess.call(str_command, shell=True)
    response_delete_temp = subprocess.call("ssh {0}@{1} \"rm temp_file\"".format(user,master_IP), shell=True)
    return


def is_period(checked_string):
    """
    Check if a string is a period.
    """
    if len(checked_string) == 1 and checked_string == '.':
        return True
    else:
        return False


def is_default_dir(checked_string):
    """
    Check if string is default Hdfs directory
    """
    if checked_string in DEFAULT_HDFS_DIR:
        return True
    else:
        return False


def check_credentials(token, auth_url=auth_url):
    """Identity,Account/Astakos. Test authentication credentials"""
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        msg = ' Authentication failed with url %s and token %s'\
            % (auth_url, token)
        raise ClientError(msg, error_authentication)
    return auth

def endpoints_and_user_id(auth):
    """
    Get the endpoints
    Identity, Account --> astakos
    Compute --> cyclades
    Object-store --> pithos
    Image --> plankton
    Network --> network
    """
    logging.log(REPORT, ' Get the endpoints')
    try:
        endpoints = dict(
            astakos=auth.get_service_endpoints('identity')['publicURL'],
            cyclades=auth.get_service_endpoints('compute')['publicURL'],
            pithos=auth.get_service_endpoints('object-store')['publicURL'],
            plankton=auth.get_service_endpoints('image')['publicURL'],
            network=auth.get_service_endpoints('network')['publicURL']
            )
        user_id = auth.user_info['id']
    except ClientError:
        msg = ' Failed to get endpoints & user_id from identity server'
        raise ClientError(msg)
    return endpoints, user_id

def init_plankton(endpoint, token):
    """
    Plankton/Initialize Imageclient.
    ImageClient has all registered images.
    """
    logging.log(REPORT, ' Initialize ImageClient')
    try:
        return ImageClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize the Image client'
        raise ClientError(msg)
