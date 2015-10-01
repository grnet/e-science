#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""orka.orka: provides entry point main()."""
import logging
import random
import string
import re
from sys import argv, stdout, stderr
from kamaki.clients import ClientError
from kamaki.clients.pithos import PithosClient
from kamaki.clients.astakos import AstakosClient
from cluster_errors_constants import *
from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS
from version import __version__
from utils import ClusterRequest, ConnectionError, authenticate_escience, get_user_clusters, \
    custom_sort_factory, custom_sort_list, custom_date_format, get_from_kamaki_conf, \
    ssh_call_hadoop, ssh_check_output_hadoop, ssh_stream_to_hadoop, \
    read_replication_factor, ssh_stream_from_hadoop, parse_hdfs_dest, get_file_protocol, \
    ssh_pithos_stream_to_hadoop, bytes_to_shorthand, from_hdfs_to_pithos, is_period, is_default_dir, \
    check_credentials, endpoints_and_user_id, init_plankton
from time import sleep
from requests.exceptions import SSLError
from ConfigParser import NoSectionError, NoOptionError


class _ArgCheck(object):
    """
    Used for type checking arguments supplied for use with type= and
    choices= argparse attributes
    """

    def __init__(self):
        self.logging_levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'summary': SUMMARY,
            'report': REPORT,
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }
        logging.addLevelName(REPORT, "REPORT")
        logging.addLevelName(SUMMARY, "SUMMARY")

    def positive_num_is(self, val):
        """
        :param val: int
        :return: val if val > 0 or raise exception
        """
        ival = int(val)
        if ival <= 0:
            raise ArgumentTypeError(" %s must be a positive number." % val)
        return ival
    
    def greater_than_min_vre_ram_is(self, val):
        """
        :param val: int
        :return: val if >= 1024 or raise exception
        """
        ival = int(val)
        if ival < vre_ram_min:
            raise ArgumentTypeError(" %s must be at least 1024 MiB for VRE servers, except for DSpace and BigBlueButton (2048 MiB)" % val)
        return ival

    def two_or_larger_is(self, val):
        """
        :param val: int
        :return: val if > 2 or raise exception
        """
        ival = int(val)
        if ival < 2:
            raise ArgumentTypeError(" %s must be at least 2." % val)
        return ival

    def five_or_larger_is(self, val):
        ival = int(val)
        if ival < 5:
            raise ArgumentTypeError(" %s must be at least 5." % val)
        return ival
    
    def a_number_is(self, val):
        """
        :param val: str
        :return val if it contains only numbers
        """
        if val.isdigit():
            return val
        else:
            raise ArgumentTypeError(" %s must be a number." % val)
        
    def a_string_is(self, val):
        """
        :param val: str
        :return val if it contains at least one letter
        """
        if not val.isdigit():
            return val
        else:
            raise ArgumentTypeError(" %s must contain at least one letter." % val)
        
    def valid_admin_password_is(self, val):
        """
        :param val: str
        :return val if string is longer than eight characters and contain only letters and numbers
        """
        if self.a_string_is(val) and re.match("^[A-Za-z0-9]{8,}$", val):
            return val
        else:
            raise ArgumentTypeError(" %s must be at least 8 characters and contain only letters and numbers." % val)


def task_message(task_id, escience_token, server_url, wait_timer, task='not_progress_bar'):
    """
    Function to check create and destroy celery tasks running from orka-CLI
    and log task state messages.
    """
    payload = {"job": {"task_id": task_id}}
    yarn_cluster_logger = ClusterRequest(escience_token, server_url, payload, action='job')
    previous_response = {'job': {'state': 'placeholder'}}
    response = yarn_cluster_logger.retrieve()
    while 'state' in response['job']:
        if response['job']['state'].replace('\r','') != previous_response['job']['state'].replace('\r',''):
            if task == 'has_progress_bar':
                stderr.write(u'{0}\r'.format(response['job']['state']))
                stderr.flush()
            else:
                stderr.write('{0}'.format('\r'))
                logging.log(SUMMARY, '{0}'.format(response['job']['state']))

            previous_response = response

        else:
            stderr.write('{0}'.format('.'))
            sleep(wait_timer)
        response = yarn_cluster_logger.retrieve()
        stderr.flush()


    if 'success' in response['job']:
        stderr.write('{0}'.format('\r'))
        return response['job']['success']

    elif 'error' in response['job']:
        stderr.write('{0}'.format('\r'))
        logging.error(response['job']['error'])
        exit(error_fatal)


class HadoopCluster(object):
    """Wrapper class for YarnCluster."""
    def __init__(self, opts):
        self.opts = opts
        try: 
            self.escience_token = authenticate_escience(self.opts['token'], self.opts['server_url'])
            self.server_url = self.opts['server_url']
        except SSLError, e:
            logging.error('Invalid SSL certificate on .kamakirc')
            exit(error_fatal)
        except ConnectionError, e:
            logging.error('e-science server unreachable or down.')
            exit(error_fatal)
        except ClientError, e:
            logging.error(e.message)
            exit(error_fatal)
    
    def create_vre_machine(self):
        """ Method for creating VRE server in~okeanos."""
        if any(image in self.opts['image'].lower() for image in ('dspace', 'bigbluebutton'))  and self.opts['ram'] < dspace_bbb_ram_min:
            logging.error('argument ram: {0} must be at least 1024 MiB for VRE servers, except for DSpace and BigBlueButton (2048 MiB).'.format(self.opts['ram']))
            exit(error_fatal)
        elif 'bigbluebutton' in self.opts['image'].lower() and self.opts['cpu'] < bbb_cpu_min:
            logging.error('argument cpu: {0} must be at least 2 for BigBlueButton.'.format(self.opts['cpu']))
            exit(error_fatal)
        try:
            payload = {"vreserver":{"project_name": self.opts['project_name'], "server_name": self.opts['name'],
                                        "cpu": self.opts['cpu'], "ram": self.opts['ram'],
                                        "disk": self.opts['disk'], "disk_template": self.opts['disk_template'], "os_choice": self.opts['image'],
                                        "admin_password": self.opts['admin_password'], "admin_email": self.opts['admin_email']}}
            yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='vre')
            response = yarn_cluster_req.post()
            if 'task_id' in response['vreserver']:
                task_id = response['vreserver']['task_id']
            else:
                logging.error(response['vreserver']['message'])
                exit(error_fatal)
            result = task_message(task_id, self.escience_token, self.server_url, wait_timer_create)
            logging.log(SUMMARY, "VRE server is active and has the following properties:")
            stdout.write("server_id: {0}\nserver_IP: {1}\n"
                         "VM root password: {2}\n".format(result['server_id'], result['server_IP'], result['VRE_VM_password']))
            if not 'bigbluebutton' in self.opts['image'].lower():
                logging.log(SUMMARY, "{0} admin user's password: {1}\n".format(filter(lambda l: l.isalpha(), self.opts['image']), self.opts['admin_password']))
            if 'dspace' in self.opts['image'].lower():
                logging.log(SUMMARY, "{0} admin user's email: {1}\n".format(filter(lambda l: l.isalpha(), self.opts['image']), self.opts['admin_email']))
            exit(SUCCESS)

        except Exception, e:
            stderr.write('{0}'.format('\r'))
            logging.error(str(e.args[0]))
            exit(error_fatal)
            
    def destroy_vre_machine(self):
        """ Method for deleting VRE servers in~okeanos."""
        vre_servers = get_user_clusters(self.opts['token'], self.opts['server_url'], choice='vreservers')
        for server in vre_servers:
            if (server['id'] == self.opts['server_id']) and server['server_status'] == const_cluster_status_active:
                break
        else:
            logging.error('Only active VRE servers can be destroyed.')
            exit(error_fatal)
        try:
            payload = {"vreserver":{"id": self.opts['server_id']}}
            yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='vre')
            response = yarn_cluster_req.delete_cluster()
            task_id = response['vreserver']['task_id']
            result = task_message(task_id, self.escience_token, self.server_url, wait_timer_delete)
            logging.log(SUMMARY, 'VRE server with name "{0}" and its IP were deleted'.format(result))
            exit(SUCCESS)
        except Exception, e:
            stderr.write('{0}'.format('\r'))
            logging.error(str(e.args[0]))
            exit(error_fatal)
    
    def vre_action(self):
        """ Method for taking an action for a Virtual Research Environment server."""
        opt_vre_create = self.opts.get('vre_create', False)
        opt_vre_destroy = self.opts.get('vre_destroy', False)

        if opt_vre_create == True:
            self.create_vre_machine()
        elif opt_vre_destroy == True:
            self.destroy_vre_machine()
        

    def create(self):
        """ Method for creating Hadoop clusters in~okeanos."""
        try:
            payload = {"clusterchoice":{"project_name": self.opts['project_name'], "cluster_name": self.opts['name'],
                                        "cluster_size": self.opts['cluster_size'],
                                        "cpu_master": self.opts['cpu_master'], "ram_master": self.opts['ram_master'],
                                        "disk_master": self.opts['disk_master'], "cpu_slaves": self.opts['cpu_slave'],
                                        "ram_slaves": self.opts['ram_slave'], "disk_slaves": self.opts['disk_slave'],
                                        "disk_template": self.opts['disk_template'], "os_choice": self.opts['image'],
                                        "replication_factor": self.opts['replication_factor'], "dfs_blocksize": self.opts['dfs_blocksize'],
                                        "admin_password": self.opts['admin_password']}}
            yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='cluster')
            response = yarn_cluster_req.create_cluster()
            if 'task_id' in response['clusterchoice']:
                task_id = response['clusterchoice']['task_id']
            else:
                logging.error(response['clusterchoice']['message'])
                exit(error_fatal)
            result = task_message(task_id, self.escience_token, self.server_url, wait_timer_create)
            logging.log(SUMMARY, "YARN Cluster is active, you can access it through {0}:8088/cluster,"
                                 " and has the following properties:".format(result['master_IP']))
            stdout.write("cluster_id: {0}\nmaster_IP: {1}\n"
                         "root password: {2}\n".format(result['cluster_id'], result['master_IP'],
                                                        result['master_VM_password']))
            if self.opts['admin_password']:
                if 'CDH' in self.opts['image']:
                    hue_user = 'hdfs'
                else:
                    hue_user = 'hduser'
                logging.log(SUMMARY, "You can access Hue browser with username {0} and password: {1}\n".format(hue_user, self.opts['admin_password']))

            exit(SUCCESS)

        except Exception, e:
            stderr.write('{0}'.format('\r'))
            logging.error(str(e.args[0]))
            exit(error_fatal)


    def destroy(self):
        """ Method for deleting Hadoop clusters in~okeanos."""
        clusters = get_user_clusters(self.opts['token'], self.opts['server_url'])
        for cluster in clusters:
            if (cluster['id'] == self.opts['cluster_id']) and cluster['cluster_status'] == const_cluster_status_active:
                break
        else:
            logging.error('Only active clusters can be destroyed.')
            exit(error_fatal)
        try:
            payload = {"clusterchoice":{"id": self.opts['cluster_id']}}
            yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='cluster')
            response = yarn_cluster_req.delete_cluster()
            task_id = response['clusterchoice']['task_id']
            result = task_message(task_id, self.escience_token, self.server_url, wait_timer_delete)
            logging.log(SUMMARY, 'Cluster with name "{0}" and all its resources deleted'.format(result))
            exit(SUCCESS)
        except Exception, e:
            stderr.write('{0}'.format('\r'))
            logging.error(str(e.args[0]))
            exit(error_fatal)
            
            
    def node_action(self):
        """ Method for taking node actions in a Hadoop cluster in~okeanos."""
        opt_addnode = self.opts.get('addnode', False)
        opt_removenode = self.opts.get('removenode', False)
        
        clusters = get_user_clusters(self.opts['token'], self.opts['server_url'])
        for cluster in clusters:
            if ((cluster['id'] == self.opts['cluster_id'])):
                if cluster['cluster_status'] == const_cluster_status_active:
                    if opt_removenode == True:
                        if int(cluster['cluster_size']) == int(cluster['replication_factor']) +1:
                            print "Limited resources. Cannot remove node."
                            exit(error_remove_node)
                        else:
                            print "Removing node"
                            new_cluster_size = int(cluster['cluster_size'])-1
                    elif opt_addnode == True:
                        print "Adding node"
                        new_cluster_size = int(cluster['cluster_size'])+1
                    else:
                        break
                    try:
                        payload = {"clusterchoice":{ 
                                    'cluster_edit': self.opts['cluster_id'],
                                    'cluster_size': new_cluster_size
                                    }}
                        yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, 
                                                          payload, action='cluster')
                        response = yarn_cluster_req.create_cluster()
                        if 'task_id' in response['clusterchoice']:
                            task_id = response['clusterchoice']['task_id']
                        else:
                            logging.error(response['clusterchoice']['message'])
                            exit(error_fatal)
                        result = task_message(task_id, self.escience_token, self.server_url, 
                                             wait_timer_create)
                        exit(SUCCESS)
                    except Exception, e:
                        stderr.write('{0}'.format('\r'))
                        logging.error(str(e.args[0]))
                        exit(error_fatal)
                else:
                    logging.error('You can take node actions only in an active cluster.')
                    exit(error_fatal)


    def hadoop_action(self):
        """ Method for applying an action to a Hadoop cluster"""
        action = str.lower(self.opts['hadoop_status'])
        clusters = get_user_clusters(self.opts['token'], self.opts['server_url'])
        active_cluster = None
        for cluster in clusters:
            if (cluster['id'] == self.opts['cluster_id']):
                active_cluster = cluster
                if cluster['cluster_status'] == const_cluster_status_active:
                    break
        else:
            logging.error('Hadoop can only be managed for an active cluster.')
            exit(error_fatal)
        if active_cluster:
            if (active_cluster['hadoop_status'] == const_hadoop_status_started and action == "start"):
                logging.error('Hadoop already started.')
                exit(error_fatal)
            elif (active_cluster['hadoop_status'] == const_hadoop_status_stopped and action == "stop"):
                logging.error('Hadoop already stopped.')
                exit(error_fatal)
        try:
            payload = {"clusterchoice":{"id": self.opts['cluster_id'], "hadoop_status": action}}
            yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='cluster')
            response = yarn_cluster_req.create_cluster()
            task_id = response['clusterchoice']['task_id']
            result = task_message(task_id, self.escience_token, self.server_url, wait_timer_delete)
            logging.log(SUMMARY, result)
            exit(SUCCESS)
        except Exception, e:
            stderr.write('{0}'.format('\r'))
            logging.error(str(e.args[0]))
            exit(error_fatal)
    
    def file_action(self):
        """ Method for taking actions to and from Hadoop filesystem """
        # safe getters, defaults to False if the option is not set
        opt_filelist = self.opts.get('filelist', False)
        opt_fileput = self.opts.get('fileput', False)
        opt_fileget = self.opts.get('fileget', False)
        opt_filemkdir = self.opts.get('filemkdir', False)
        if opt_filelist == True:
            self.list_pithos_files()
        else:
            clusters = get_user_clusters(self.opts['token'], self.opts['server_url'])
            active_cluster = None
            for cluster in clusters:
                if (cluster['id'] == self.opts['cluster_id']):
                    if cluster['hadoop_status'] == const_hadoop_status_started:
                        active_cluster = cluster
                        break
            else:
                logging.error('You can take file actions on active clusters with started hadoop only.')
                exit(error_fatal)
            if opt_fileput == True:
                try:
                    sourcesLength = len(self.opts['destination'])
                    sources = [self.opts['source']]
                    destination = self.opts['destination'][-1]
                    if sourcesLength > 1:
                        if not destination.endswith("/"):
                            destination += '/'
                        for source in self.opts['destination'][:-1]:
                            sources.append(source)
                    for self.opts['source'] in sources:
                        self.opts['destination'] = destination
                        source_path = self.opts['source'].split("/")
                        self.source_filename = source_path[len(source_path)-1]
                        if is_period(self.opts['destination']) or is_default_dir(self.opts['destination']):
                            self.opts['destination'] = self.source_filename
                        file_protocol, remain = get_file_protocol(self.opts['source'], 'fileput', 'source')
                        self.check_hdfs_destination(active_cluster)
                        if file_protocol == 'http-ftp':
                            self.put_from_server()
                        elif file_protocol == 'file':
                            self.put_from_local(active_cluster)
                        elif file_protocol == 'pithos':
                            kamaki_filespec = remain
                            self.put_from_pithos(active_cluster, kamaki_filespec)
                        else:
                            logging.error('Unrecognized source filespec.')
                            exit(error_fatal)
                        
                except Exception, e:
                    stderr.write('{0}'.format('\r'))
                    logging.error(str(e.args[0]))
                    exit(error_fatal)
            elif opt_fileget == True:
                try:
                    if is_period(self.opts['destination']):
                        self.opts['destination'] = os.getcwd()
                    file_protocol, remain = get_file_protocol(self.opts['destination'], 'fileget', 'destination')
                    if file_protocol == 'pithos':
                        self.get_from_hadoop_to_pithos(active_cluster, remain)
                    elif file_protocol == 'file' or file_protocol == "folder":
                        self.get_from_hadoop_to_local(active_cluster)
                    else:
                        logging.error('Unrecognized destination filespec.')
                        exit(error_fatal)
                except Exception, e:
                    stderr.write('{0}'.format('\r'))
                    logging.error(str(e.args[0]))
                    exit(error_fatal)
            elif opt_filemkdir == True:
                try:
                    file_protocol, remain = get_file_protocol(self.opts['directory'], 'filemkdir', 'destination')
                    if file_protocol == "hdfs":
                        if self.opts['recursive'] == True:
                            str_command = " dfs -mkdir -p \"{0}\"".format(remain)
                        else:
                            str_command = " dfs -mkdir \"{0}\"".format(remain)
                        retcode = ssh_call_hadoop("hduser", active_cluster['master_IP'], str_command)
                        if str(retcode) == str(SUCCESS):
                            logging.log(SUMMARY, "\"{0}\" created.".format(remain))
                            exit(SUCCESS)
                        else:
                            logging.log(SUMMARY, "\"{0}\" not created. Use -p for a nested destination.".format(remain))
                    else:
                        logging.error('Invalid destination filesystem.')
                        exit(error_fatal)
                except Exception, e:
                    stderr.write('{0}'.format('\r'))
                    logging.error(str(e.args[0]))
                    exit(error_fatal)
            
                
    def list_pithos_files(self):
        """ Method for listing pithos+ files available to the user """
        auth_url = self.opts['auth_url']
        token = self.opts['token']
        try:
            auth = AstakosClient(auth_url, token)
            auth.authenticate()
        except ClientError:
            msg = 'Authentication error: Invalid Token'
            logging.error(msg)
            exit(error_fatal)
        pithos_endpoint = auth.get_endpoint_url('object-store')
        pithos_container = self.opts.get('pithos_container','pithos')
        user_id = auth.user_info['id']
        pithos_client = PithosClient(pithos_endpoint,self.opts['token'], user_id, pithos_container)
        objects = pithos_client.list_objects()
        for object in objects:
            is_dir = 'application/directory' in object.get('content_type', object.get('content-type', ''))
            is_dir = 'application/folder' in object.get('content_type', object.get('content-type', ''))
            if not is_dir:
                print u"{:>12s} \"pithos:/{:s}/{:s}\"".format(bytes_to_shorthand(object['bytes']),
                                                              pithos_container,object['name'])

    def check_hdfs_destination(self, cluster):
        """
        Method checking the Hdfs destination argument for existence and type (directory or file).
        """
        parsed_path = parse_hdfs_dest("(.+/)[^/]+$", self.opts['destination'])
        if parsed_path:
            # if directory path ends with filename, checking if both exist
            try:
                self.check_hdfs_path(cluster['master_IP'], parsed_path, '-d')
            except SystemExit:
                msg = 'Target directory does not exist. Aborting upload'
                raise RuntimeError(msg)
            try:
                self.check_hdfs_path(cluster['master_IP'], self.opts['destination'], '-d')
            except SystemExit:
                self.check_hdfs_path(cluster['master_IP'], self.opts['destination'], '-e')
                return 0

            self.opts['destination'] += '/{0}'.format(self.source_filename)
            self.check_hdfs_path(cluster['master_IP'], self.opts['destination'], '-e')
        elif self.opts['destination'].endswith("/") and len(self.opts['destination']) > 1:
            # if only directory is given
            try:
                self.check_hdfs_path(cluster['master_IP'], self.opts['destination'], '-d')
            except SystemExit:
                msg = 'Target directory does not exist. Aborting upload'
                raise RuntimeError(msg)
            self.check_hdfs_path(cluster['master_IP'], self.opts['destination'] + self.source_filename, '-e')
            self.opts['destination'] += self.source_filename
        # if destination is default directory /user/hduser, check if file exists in /user/hduser.
        else:
            self.check_hdfs_path(cluster['master_IP'], self.opts['destination'], '-e')


    def put_from_pithos(self, cluster, sourcefile):
        """ Method for transferring pithos+ files to Hadoop filesystem """
        """ Streaming """
        logging.log(SUMMARY, 'Start transferring pithos file to hdfs' )
        pithos_url = ssh_pithos_stream_to_hadoop("hduser", cluster['master_IP'],
                              sourcefile, self.opts['destination'])
        if pithos_url:
            self.opts['source'] = pithos_url
            result = self.put_from_server()
            if result == 0:
                logging.log(SUMMARY, 'Pithos+ file uploaded to Hadoop filesystem' )
            else:
                logging.log(SUMMARY, 'There was a problem uploading to Hadoop')
            # cleanup
            ssh_pithos_stream_to_hadoop("hduser", cluster['master_IP'],
                              sourcefile, self.opts['destination'], False)


    def check_hdfs_path(self, master_IP, dest, option):
        """
        Check if a path exists in Hdfs 0: exists, 1: doesn't exist
        """
        path_exists = ssh_call_hadoop("hduser", master_IP, " dfs -test " + option + " " + "\'" + dest + "\'")
        if option == '-e' and path_exists == 0:
            logging.error('File already exists. Aborting upload.')
            exit(error_fatal)
        elif option == '-d' and path_exists != 0:
            exit(error_fatal)
        return path_exists

    def put_from_local(self, cluster):
        """ Put local files to Hdfs."""
        if os.path.isfile(self.opts['source']):
            file_size = os.path.getsize(self.opts['source'])
        else:
            msg = 'File {0} does not exist'.format(self.opts['source'])
            raise IOError(msg)

        # check available free space in hdfs
        report = ssh_check_output_hadoop("hduser", cluster['master_IP'], " dfsadmin -report / ")
        for line in report:
            if line.startswith('DFS Remaining'):
                tokens = line.split(' ')
                dfs_remaining = tokens[2]
                break
        # read replication factor
        replication_factor = read_replication_factor("hduser", cluster['master_IP'])

        # check if file can be uploaded to hdfs
        if file_size * replication_factor > int(dfs_remaining):
            logging.log(SUMMARY, 'File too big to be uploaded' )
            exit(error_fatal)

        else:
            """ Streaming """
            logging.log(SUMMARY, "Start uploading file '{0}' to hdfs".format(self.source_filename))
            ssh_stream_to_hadoop("hduser", cluster['master_IP'],
                                  self.opts['source'], self.opts['destination'])

            logging.log(SUMMARY, 'Local file uploaded to Hadoop filesystem' )


    def put_from_server(self):
        """
        Put files from ftp/http server to Hdfs. Send a POST request to orka app server to
        copy the ftp/http file to the requested
        """
        payload = {"hdfs":{"id": self.opts['cluster_id'], "source": "\'{0}\'".format(self.opts['source']),
                                        "dest": "\'{0}\'".format(self.opts['destination']), "user": self.opts['user'],
                                        "password": self.opts['password']}}

        yarn_cluster_req = ClusterRequest(self.escience_token, self.server_url, payload, action='hdfs')
        response = yarn_cluster_req.post()
        if 'task_id' in response['hdfs']:
            task_id = response['hdfs']['task_id']
        else:
            logging.error(response['hdfs']['message'])
            exit(error_fatal)
        logging.log(SUMMARY, 'Starting file transfer')
        result = task_message(task_id, self.escience_token, self.server_url, wait_timer_delete,
                                  task='has_progress_bar')
        if result == 0:
            stdout.flush()
            logging.log(SUMMARY, 'Transfered file to Hadoop filesystem')
            return result
    
    def get_from_hadoop_to_pithos(self, cluster, destination_path):
        """ Method for getting files from Hadoop clusters in ~okeanos to pithos filesystem."""
        try:
            file_exists = ssh_call_hadoop("hduser", cluster['master_IP'],
                                      " dfs -test -e " + "\'{0}\'".format(self.opts['source']))
            if file_exists == 0:
                logging.log(SUMMARY, 'Start downloading file from hdfs')
                from_hdfs_to_pithos("hduser", cluster['master_IP'],
                                  self.opts['source'], destination_path)
            else:
                logging.error('File does not exist.')
                exit(error_fatal) 
        except Exception, e:
            logging.error(str(e.args[0]))
            exit(error_fatal)
    
    def get_from_hadoop_to_local(self, cluster):
        """ Method for getting files from Hadoop clusters in ~okeanos to local filesystem."""
        source = self.opts['source']
        destination = self.opts['destination']
        try:
            logging.log(SUMMARY, "Checking if \'{0}\' exists in Hadoop filesystem.".format(source))
            src_file_exists = ssh_call_hadoop("hduser", cluster['master_IP'],
                                      " dfs -test -e " + "\'{0}\'".format(source))
            
            if src_file_exists == 0:
                src_base_folder, src_file = os.path.split(source)
                dest_base_folder, dest_top_file_or_folder = os.path.split(destination)
                if os.path.exists(destination):
                    if os.path.isfile(destination):
                        logging.log(SUMMARY, "\'{0}\' already exists.".format(destination))
                        exit(error_fatal)
                    elif os.path.isdir(destination):
                        destination = os.path.join(destination,src_file)
                        if os.path.exists(destination):
                            logging.log(SUMMARY, "\'{0}\' already exists.".format(destination))
                            exit(error_fatal)
                else:
                    try:
                        if dest_base_folder:
                            if not os.path.exists(dest_base_folder):
                                os.makedirs(dest_base_folder)
                            destination = os.path.join(dest_base_folder,src_file)
                        else:
                            if dest_top_file_or_folder.endswith("/"):
                                destination = os.path.join(dest_top_file_or_folder,src_file)
                            else:
                                destination = dest_top_file_or_folder
                    except OSError:
                        logging.error('Choose another destination path-directory.')
                        exit(error_fatal)
                
                logging.log(SUMMARY, 'Start downloading file from hdfs')
                ssh_stream_from_hadoop("hduser", cluster['master_IP'],
                                       source, destination)
                
            else:
                logging.error('Source file does not exist.')
                exit(error_fatal) 

            if os.path.exists(destination):
                logging.log(SUMMARY, 'File downloaded from Hadoop filesystem.')
            else:
                logging.error('Error while downloading from Hadoop filesystem.')
        
        except Exception, e:
            logging.error(str(e.args[0]))
            exit(error_fatal)


class UserClusterVreInfo(object):
    """ Class holding user cluster and VRE info
    sortdict: input a cluster or VRE dictionary, output cluster or VRE respectively with keys sorted according to order
    sortlist: input a clusters or VREs list of cluster or VRE dictionaries, output a clusters or VREs list respectively sorted according to cluster or VRE key
    list: pretty printer
    """
    def __init__(self, opts):
        self.opts = opts
        self.data = list()
        self.cluster_list_order = [['cluster_name','id','action_date','cluster_size','cluster_status','hadoop_status',
                            'master_IP','project_name','os_image','disk_template',
                            'cpu_master','ram_master','disk_master',
                            'cpu_slaves','ram_slaves','disk_slaves']]
        self.vre_list_order = [['server_name', 'id', 'action_date', 'server_status', 'server_IP', 'project_name', 'os_image',
                                 'disk_template', 'cpu', 'ram', 'disk']]
        self.sort_vre_func = custom_sort_factory(self.vre_list_order)
        self.vre_short_list = {'id':True, 'server_name':True, 'action_date':True,
                                   'server_status':True, 'server_IP':True}
        self.sort_cluster_func = custom_sort_factory(self.cluster_list_order)
        self.cluster_short_list = {'id':True, 'cluster_name':True, 'action_date':True, 'cluster_size':True,
                                   'cluster_status':True, 'hadoop_status':True, 'master_IP':True}
        self.skip_list = {'task_id':True, 'state':True}
        self.status_desc_to_status_id = {'ACTIVE':'1', 'PENDING':'2', 'DESTROYED':'0', 'FAILED':'3'}
        self.status_id_to_status_desc = {'1':'ACTIVE', '2':'PENDING', '0':'DESTROYED', '3':'FAILED'}
        self.hdp_status_id_to_status_desc = {'0':'STOPPED','1':'STARTED','2':'FORMAT'}
        self.hdp_status_desc_to_status_id = {'STOPPED':'0','STARTED':'1','FORMAT':'2'}
        self.disk_template_to_label = {'ext_vlmc':'Archipelago', 'drbd':'Standard'}
        self.list_order = ['id']

    def sortdict(self, cluster_or_vre):
        if self.type == 'server':
            return self.sort_vre_func(cluster_or_vre)
        return self.sort_cluster_func(cluster_or_vre)
    
    def sortlist(self, clusters_or_vres, keys):
        return custom_sort_list(clusters_or_vres, keys)
    
    def list(self, type, choice_argument):
        self.type = type
        short_list = self.cluster_short_list
        if type == 'server':
            short_list = self.vre_short_list
        try:
            self.data.extend(get_user_clusters(self.opts['token'], self.opts['server_url'], choice=choice_argument))
        except ClientError, e:
            logging.error(e.message)
            exit(error_fatal)
        except Exception, e:
            logging.error(str(e.args[0]))
            exit(error_fatal)
        
        opt_short = not self.opts['verbose']
        opt_status = False
        opt_id = self.opts.get('{0}_id'.format(type), False)
        count = 0
        if self.opts['status']:
            opt_status = self.status_desc_to_status_id[self.opts['status'].upper()]
        
        if len(self.data) > 0:
            sorted_list = self.sortlist(self.data, self.list_order)
            for cluster_or_vre in sorted_list:
                if opt_status and cluster_or_vre['{0}_status'.format(type)] != opt_status:
                    continue
                if opt_id and cluster_or_vre['id'] != opt_id:
                    continue
                count += 1
                sorted_cluster_or_vre = self.sortdict(cluster_or_vre)
                for key in sorted_cluster_or_vre:
                    if (opt_short and not short_list.has_key(key)) or self.skip_list.has_key(key):
                        continue
                    # using string.format spec mini-language to create a hanging indent 
                    # https://docs.python.org/2/library/string.html#formatstrings
                    if key == '{0}_name'.format(type):
                        fmt_string = u'{:<5}' + key + ': {' + key + '}'
                    elif key == '{0}_status'.format(type):
                        fmt_string = '{:<10}' + key + ': ' + self.status_id_to_status_desc[sorted_cluster_or_vre[key]]
                    elif key == 'hadoop_status':
                        fmt_string = '{:<10}' + key + ': ' + self.hdp_status_id_to_status_desc[sorted_cluster_or_vre[key]]
                    elif key == 'disk_template':
                        fmt_string = '{:<10}' + key + ': ' + self.disk_template_to_label[sorted_cluster_or_vre[key]]
                    elif key == 'action_date':
                        fmt_string = '{:<10}' + key + ': ' + custom_date_format(sorted_cluster_or_vre[key])
                    else:
                        fmt_string = '{:<10}' + key + ': {' + key + '}'
                    print fmt_string.format('',**sorted_cluster_or_vre)
                print ''
            if count == 0:
                print 'No {0}(s) found matching those options.'.format(type)
        else:
            print 'No user {0} Information available.'.format(type)

class ImagesInfo(object):
    """ Class holding info for available images"""
    
    def __init__(self, opts):
        self.opts = opts
        self.image_list = []             
             
    def get_images(self,images):
        """Method for getting the images available in database"""
        response = ClusterRequest('', self.opts['server_url'], '', images['action']).retrieve()
        return response[images['resource_name']]
          
    def list_images(self, images_type):
        """Method for listing the images available in database"""
        images = {}
        if images_type == 'vre':
            images =  VRE_IMAGES
        elif images_type == 'orka':
            images = ORKA_IMAGES
        self.image_list = self.get_images(images)
        for image in self.image_list:
            self.list_image(image)
                       
    def list_image(self,image):
        """Method for listing info about one image"""
        print '{0}: {1}'.format('name',image['image_name'])
        print '{0}: {1}\n'.format('pithos uuid',image['image_pithos_uuid'])
            
    
def main():
    """
    Entry point of orka package. Parses user arguments and return
    appropriate messages for success or error.
    """
    orka_parser = ArgumentParser(description='Manage a Hadoop-Yarn'
                                        ' cluster or a Virtual Research Environment server in ~okeanos ')
    checker = _ArgCheck()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                                level=checker.logging_levels[default_logging],
                                datefmt='%Y-%m-%d %H:%M:%S')
    try:
        kamaki_token = get_from_kamaki_conf('cloud "~okeanos"', 'token')
        kamaki_base_url = get_from_kamaki_conf('orka','base_url')
    except (NoSectionError, NoOptionError), e:
        kamaki_token = ' '
        kamaki_base_url = ' '
        logging.warning(e.message)
    auto_generated_pass = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(12))
    
    orka_subparsers = orka_parser.add_subparsers(help='Choose Hadoop cluster or VRE server action')
    orka_parser.add_argument("-V", "--version", action='version',
                        version=('orka %s' % __version__))
    # add commands shared by all subparsers so we don't have to duplicate them
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument("--token", metavar='token', default=kamaki_token, type=checker.a_string_is,
                              help='Synnefo authentication token. Default read from .kamakirc')
    common_parser.add_argument("--auth_url", metavar='auth_url', default=auth_url,
                              help='Synnefo authentication url. Default is ' +
                              auth_url)
    common_parser.add_argument("--server_url", metavar='server_url', default=kamaki_base_url,
                              help='Application server url.  Default read from .kamakirc')
    
    common_create_parser = ArgumentParser(add_help=False)
      
    common_create_parser.add_argument("name", help='The specified name of the cluster or Virtual Research Environment'
                              ' server. Will be prefixed by [orka]', type=checker.a_string_is)

    # images
    parser_images = orka_subparsers.add_parser('images', parents=[common_parser],
                                     help='List available Hadoop images.')
    # cluster actions group
    parser_create = orka_subparsers.add_parser('create', parents=[common_parser, common_create_parser],
                                     help='Create a Hadoop-Yarn cluster'
                                   ' on ~okeanos.')
    parser_vre = orka_subparsers.add_parser('vre', help='Operations for Virtual Research Environment machines'
                                     ' on ~okeanos.')
    vre_subparsers = parser_vre.add_subparsers(help='Choose VRE server action create, destroy or list available VRE images')
    # create VRE server parser
    parser_vre_create = vre_subparsers.add_parser('create', parents=[common_parser, common_create_parser],
                                                  help='Create a Virtual Research Environment server'
                                     ' on ~okeanos.')
    parser_vre_destroy = vre_subparsers.add_parser('destroy', parents=[common_parser],
                                                  help='Destroy a Virtual Research Environment server'
                                     ' on ~okeanos.')
    parser_vre_images = vre_subparsers.add_parser('images', parents=[common_parser],
                                                  help='List available Virtual Research Environment images')
    parser_vre_list = vre_subparsers.add_parser('list', parents=[common_parser],
                                                  help='List user Virtual Research Environment servers')
    parser_destroy = orka_subparsers.add_parser('destroy', parents=[common_parser],
                                     help='Destroy a Hadoop-Yarn cluster'
                                     ' on ~okeanos.')
    parser_node = orka_subparsers.add_parser('node', parents=[common_parser],
                                     help='Operations on a Hadoop-Yarn cluster for adding or deleting a node.')
    parser_list = orka_subparsers.add_parser('list', parents=[common_parser],
                                     help='List user clusters.')
    parser_info = orka_subparsers.add_parser('info', parents=[common_parser],
                                     help='Information for a specific Hadoop-Yarn cluster.')
    # hadoop actions group
    parser_hadoop = orka_subparsers.add_parser('hadoop',parents=[common_parser],
                                     help='Start, Stop or Format a Hadoop-Yarn cluster.')
    # hadoop filesystem actions group
    parser_file = orka_subparsers.add_parser('file', parents=[common_parser],
                                        help='File operations between various file sources and Hadoop-Yarn filesystem.')
    file_subparsers = parser_file.add_subparsers(help='Choose file action put, get or list')
    parser_file_put = file_subparsers.add_parser('put', parents=[common_parser], usage='%(prog)s cluster_id source [source ...] destination',
                                     help='Put/Upload a file from <source> to the Hadoop-Yarn filesystem.')
    parser_file_mkdir = file_subparsers.add_parser('mkdir',parents=[common_parser],
                                                   help='Create a directory on the Hadoop-Yarn filesystem')
    parser_file_get = file_subparsers.add_parser('get',parents=[common_parser],
                                     help='Get/Download a file from the Hadoop-Yarn filesystem to <destination>.')
    parser_file_list = file_subparsers.add_parser('list',parents=[common_parser],
                                             help='List pithos+ files.')
    parser_node_subparsers = parser_node.add_subparsers(help='Choose node action add or delete')
    parser_addnode = parser_node_subparsers.add_parser('add',
                                                       help='Add a node in a Hadoop-Yarn cluster on ~okeanos.')
    parser_removenode = parser_node_subparsers.add_parser('remove',
                                                          help='Remove a node from a Hadoop-Yarn cluster on ~okeanos.')
    
    if len(argv) > 1:
        
        parser_create.add_argument("cluster_size", help='Total number of cluster nodes',
                              type=checker.two_or_larger_is)
        parser_create.add_argument("cpu_master", help='Number of CPU cores for the master node of a cluster',
                                   type=checker.positive_num_is)
        parser_create.add_argument("ram_master", help='Size of RAM (MB) for the master node of a cluster',
                                   type=checker.positive_num_is)
    
        parser_create.add_argument("disk_master", help='Disk size (GB) for the master node of a cluster',
                                   type=checker.five_or_larger_is)
        parser_create.add_argument("cpu_slave", help='Number of CPU cores for the slave node(s)',
                              type=checker.positive_num_is)
        parser_create.add_argument("ram_slave", help='Size of RAM (MB) for the slave node(s)',
                              type=checker.positive_num_is)
        parser_create.add_argument("disk_slave", help='Disk size (GB) for the slave node(s)',
                              type=checker.five_or_larger_is)
        parser_create.add_argument("disk_template", help='Disk template (choices: {%(choices)s})',
                              metavar='disk_template', choices=['Standard', 'Archipelago'], 
                              type=str.capitalize)
        parser_create.add_argument("project_name", help='~okeanos project name'
                              ' to request resources from ', type=checker.a_string_is)
        parser_create.add_argument("--image", help='OS for the cluster.'
                              ' Default is "Debian Base"', metavar='image',
                              default=default_image)
        
        parser_create.add_argument("--replication_factor", metavar='replication_factor', default=2, type=checker.positive_num_is,
                              help='Replication factor for HDFS. Must be between 1 and number of slave nodes (cluster_size -1). Default is 2.')
        parser_create.add_argument("--dfs_blocksize", metavar='dfs_blocksize', default=128, type=checker.positive_num_is,
                              help='HDFS block size (in MB). Default is 128.')
        parser_create.add_argument("--admin_password", metavar='admin_password', default=auto_generated_pass, type=checker.valid_admin_password_is,
                              help='Admin password for Hue login. Default is auto-generated')
        
        parser_destroy.add_argument('cluster_id',
                              help='The id of the Hadoop cluster', type=checker.positive_num_is)
        
        parser_vre_create.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='vre_create')
        parser_vre_create.add_argument("cpu", help='Number of CPU cores for VRE server. Must be at least 2 for BigBlueButton.',
                                   type=checker.positive_num_is)
        parser_vre_create.add_argument("ram", help='Size of RAM (MB) for VRE servers must be at least 1024 MiB, except for DSpace and BigBlueButton (2048 MiB)',
                                   type=checker.greater_than_min_vre_ram_is)
    
        parser_vre_create.add_argument("disk", help='Disk size (GB) for VRE server',
                                   type=checker.five_or_larger_is)
        parser_vre_create.add_argument("disk_template", help='Disk template (choices: {%(choices)s})',
                              metavar='disk_template', choices=['Standard', 'Archipelago'], 
                              type=str.capitalize)
        parser_vre_create.add_argument("project_name", help='~okeanos project name'
                              ' to request resources from ', type=checker.a_string_is)
        parser_vre_create.add_argument("image", help='OS for the VRE server.', metavar='image')
        parser_vre_create.add_argument("--admin_password", metavar='admin_password', default=auto_generated_pass, type=checker.valid_admin_password_is,
                              help='Admin password for VRE servers. Default is auto-generated')
        parser_vre_create.add_argument("--admin_email", metavar='admin_email', default='admin@example.com', type=checker.a_string_is,
                              help='Admin email for VRE DSpace image. Default is admin@example.com')
        
        
        parser_vre_destroy.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='vre_destroy')
        
        parser_vre_destroy.add_argument('server_id',
                              help='The id of a VRE server', type=checker.positive_num_is)
        
        parser_vre_list.add_argument('--status', help='Filter by status ({%(choices)s})'
                              ' Default is all: no filtering.', type=str.upper,
                              metavar='status', choices=['ACTIVE','DESTROYED','PENDING'])
        parser_vre_list.add_argument('--verbose', help='List extra Virtual Research Environment server details.',
                              action="store_true")
        

        # hidden argument with default value so we can set opts['addnode'] 
        # when ANY 'orka node add' command is invoked
        parser_addnode.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='addnode')
        parser_addnode.add_argument('cluster_id', help='The id of the Hadoop cluster where the node will be added',
                                   type=checker.positive_num_is)

        # hidden argument with default value so we can set opts['removenode'] 
        # when ANY 'orka node remove' command is invoked
        parser_removenode.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='removenode')
        parser_removenode.add_argument('cluster_id', help='The id of the Hadoop cluster where the node will be removed', 
                                       type=checker.positive_num_is)

        parser_list.add_argument('--status', help='Filter by status ({%(choices)s})'
                              ' Default is all: no filtering.', type=str.upper,
                              metavar='status', choices=['ACTIVE','DESTROYED','PENDING'])
        parser_list.add_argument('--verbose', help='List extra cluster details.',
                              action="store_true")         
        
        
        parser_hadoop.add_argument('hadoop_status', 
                              help='Hadoop status (choices: {%(choices)s})', type=str.lower,
                              metavar='hadoop_status', choices=['start', 'format', 'stop'])
        parser_hadoop.add_argument('cluster_id',
                              help='The id of the Hadoop cluster', type=checker.positive_num_is)

        parser_info.add_argument('cluster_id',
                                 help='The id of the Hadoop cluster', type=checker.positive_num_is)

        # hidden argument with default value so we can set opts['fileput'] 
        # when ANY 'orka file put' command is invoked
        parser_file_put.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='fileput')
        parser_file_put.add_argument('cluster_id',
                              help='The id of the Hadoop cluster', type=checker.positive_num_is)
        parser_file_put.add_argument('source',
                              help='The files (local, pithos, ftp) to be uploaded')
        parser_file_put.add_argument('destination', nargs="+",
                              help='Destination in the Hadoop filesystem')
        parser_file_put.add_argument('--user',
                              help='Ftp-Http remote user')
        parser_file_put.add_argument('--password',
                              help='Ftp-Http password')
        
        parser_file_mkdir.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='filemkdir')
        parser_file_mkdir.add_argument('cluster_id',
                                       help='The id of the Hadoop cluster', type=checker.positive_num_is)
        parser_file_mkdir.add_argument('directory',
                                       help='Directory to create on HDFS')
        parser_file_mkdir.add_argument('-p', action='store_true', dest='recursive',
                                       help='Recursive target directory creation')
        
        # hidden argument with default value so we can set opts['fileget'] 
        # when ANY 'orka file get' command is invoked
        parser_file_get.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='fileget')
        parser_file_get.add_argument('cluster_id',
                              help='The id of the Hadoop cluster', type=checker.positive_num_is)
        parser_file_get.add_argument('source',
                              help='The file to be downloaded')
        parser_file_get.add_argument('destination',
                              help='Destination in Local or Pithos+ filesystem')
        
        # add a hidden argument with default value so we can set opts['filelist'] 
        # by simply invoking parser_file_list without arguments 'orka file list'
        # orka file list command runs against pithos+ so doesn't need cluster info
        parser_file_list.add_argument('--foo', nargs="?", help=SUPPRESS, default=True, dest='filelist')
        parser_file_list.add_argument('--container', metavar='container', default='/pithos', dest='pithos_container',
                                      help='Pithos+ container name. Default is "pithos". (kamaki container list)')
                
        opts = vars(orka_parser.parse_args(argv[1:]))
        c_hadoopcluster = HadoopCluster(opts)
        c_userservers = UserClusterVreInfo(opts)
        c_imagesinfo = ImagesInfo(opts)
        verb = argv[1]
        if verb == 'create':
            if opts['cluster_size'] == 2:
                if opts['replication_factor'] != 1:
                    logging.warning('Replication factor cannot exceed the number of slave nodes; defaulting to 1')
                    opts['replication_factor'] = 1
            if opts['cluster_size'] <= opts['replication_factor']:
                logging.error('Replication factor must be between 1 and number of slave nodes (cluster_size -1)')
                exit(error_replication_factor)
            if opts['image'] in images_without_hue:
                opts['admin_password'] = ''
            c_hadoopcluster.create()
        elif verb == 'destroy':
            c_hadoopcluster.destroy()
        elif verb == 'images':
            c_imagesinfo.list_images('orka')
        elif verb == 'list' or verb == 'info':
            if verb == 'info':
                opts['verbose'] = True
                opts['status'] = None
            c_userservers.list('cluster', 'clusters')       
        elif verb == 'hadoop':
            c_hadoopcluster.hadoop_action()
        elif verb == 'file':
            c_hadoopcluster.file_action()
        elif verb == 'vre':
            if argv[2] == 'images':
                c_imagesinfo.list_images('vre')
            elif argv[2] == 'list':
                c_userservers.list('server', 'vreservers')
            else:
                c_hadoopcluster.vre_action()
        elif verb == 'node':
            c_hadoopcluster.node_action()

    else:
        logging.error('No arguments were given')
        orka_parser.parse_args(' -h'.split())
        exit(error_no_arguments)
         

if __name__ == "__main__":
    main()
