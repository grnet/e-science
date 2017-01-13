#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script manages an Orka server image.

@author: e-science Dev-team
"""
from sys import argv
from datetime import datetime
import os
import yaml
import sys
import random, string
import base64
from time import sleep
import logging
import subprocess
from base64 import b64encode
from os.path import abspath, join, expanduser, basename, dirname
from kamaki.clients import ClientError
from kamaki.clients.image import ImageClient
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesClient, CycladesNetworkClient
from kamaki.clients.utils import https
from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS

# Globals and errors
https.patch_ignore_ssl()
error_fatal = -1
REPORT = 25
SUMMARY = 29
auth_url = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
MAX_WAIT=300
default_logging = 'report'
UUID_FILE = 'permitted_uuids.txt'
ENCRYPT_FILE = 'encrypt_key.py'


class _logger(object):
    """Used for initializing logging object"""

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

    def valid_file_is(self, val):
        """
        :param val: str
        :return val if val is a valid filename
        """
        val = val.replace('~', os.path.expanduser('~'))
        if os.path.isfile(val):
            return val
        else:
            raise ArgumentTypeError(" %s file does not exist." % val)
        
def check_credentials(token, auth_url=auth_url):
    """Identity,Account/Astakos. Test authentication credentials"""
    
    logging.log(REPORT, ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
    except ClientError:
        msg = ' Authentication failed with url %s and token %s'\
            % (auth_url, token)
        raise ClientError(msg, error_fatal)
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


def init_cyclades_netclient(endpoint, token):
    """
    Initialize CycladesNetworkClient
    Cyclades Network client needed for all network functions
    e.g. create network,create floating IP
    """
    
    logging.log(REPORT, ' Initialize a cyclades network client')
    try:
        return CycladesNetworkClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades network client'
        raise ClientError(msg)


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


def init_cyclades(endpoint, token):
    """
    Compute / Initialize Cyclades client.CycladesClient is used
    to create virtual machines
    """
    
    logging.log(REPORT, ' Initialize a cyclades client')
    try:
        return CycladesClient(endpoint, token)
    except ClientError:
        msg = ' Failed to initialize cyclades client'
        raise ClientError(msg)
    
def personality(ssh_keys_path=''):
        """Personality injects ssh keys to the virtual machines we create"""       
        personality = []
        if ssh_keys_path:
            try:
                keys_path = ssh_keys_path
                with open(abspath(keys_path)) as f:
                    personality.append(dict(
                        contents=b64encode(f.read()),
                        path='/root/.ssh/authorized_keys',
                        owner='root', group='root', mode=0600))
            except IOError:
                msg = " No valid public ssh key(id_rsa.pub) in " + (abspath(keys_path))
                raise IOError(msg)
        if ssh_keys_path:
                personality.append(dict(
                    contents=b64encode('StrictHostKeyChecking no'),
                    path='/root/.ssh/config',
                    owner='root', group='root', mode=0600))
        return personality

def query_yes_no(question, default="yes"):
    """Ask a yes/no question and return the answer.
    "default" is the presumed answer if the user just hits <Enter>.
    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

class OrkaServer(object):
    """
    Class for starting an Orka Server
    """
    def __init__(self, opts):
        """Initialization of OrkaServer data attributes"""
        self.opts = opts
        # load the sensitive data from the yaml file
        with open(self.opts['file'], 'r') as f:
            self.script = yaml.load(f)     
        # remove file
        response = query_yes_no("Should the file " + self.opts['file'] + " be deleted? If you choose yes, make sure you have taken the necessary steps to remember your passwords.")
        if response:
            os.remove(self.opts['file'])

    def check_pass_length(self, password):
        """
        Function that checks the length of passwords.
        Passwords should contain at least 8 characters
        """
        if len(password) < 8:
            print 'Passwords should contain at least 8 characters'
            exit(error_fatal)
        else:
            return password
        
    def create_ansible_hosts(self):
        """
        Function that creates the ansible_hosts file and
        returns the name of the file.
        """
        hosts_filename = os.getcwd() + '/ansible_hosts'
        host = '[webserver]'
        with open(hosts_filename, 'w+') as target:
            target.write(host + '\n')
            target.write('localhost ansible_ssh_host=127.0.0.1')
            
        return hosts_filename
    
    def create_permitted_uuids_file(self,uuid):
        """
        Create the file that contains the permitted ~okeanos uuids for orka login.
        """
        PROJECT_PATH = join(dirname(abspath(__file__)), '..')
        FILE_PATH = join(PROJECT_PATH,UUID_FILE)
        with open(FILE_PATH,'a+') as target:
            target.write(uuid + '\n')
        return 0
        
    def create_encrypt_file(self,uuid):
        """
        Create the file that is used for token encryption in database.
        Key value is equal to timestamp plus okeanos user uuid plus six random chars.
        """
        random_chars = ''.join(random.choice(string.lowercase) for i in range(6))
        timestamp = datetime.now().strftime('%Y/%m/%d%H:%M:%S')
        random_key = timestamp + uuid + random_chars
        PROJECT_BACKEND_PATH = join(dirname(abspath(__file__)), '../webapp/backend')
        FILE_PATH = join(PROJECT_BACKEND_PATH,ENCRYPT_FILE)
        with open(FILE_PATH,'a+') as target:
            target.write('#!/usr/bin/env python\n')
            target.write('# -*- coding: utf-8 -*-\n\n')
            target.write('key = "{0}"'.format(random_key))
        return 0
    
    def create_secret_key(self):
        """
        Return a string of 50 random chars to be used as secret key in django.
        """
        return ''.join(random.choice(string.lowercase) for i in range(50))

        
    def action(self,verb):
        """
        Executes an action on orka server
        """
        self.ansible_sudo_pass = self.script.get("orka_admin_password")
        self.create_ansible_hosts()
        vars = 'ansible_ssh_pass={0} ansible_sudo_pass={0}'.format(self.ansible_sudo_pass)
        tag = verb
        if verb == 'start':
            self.db_password = self.check_pass_length(self.script.get("postgresql_password"))
            self.django_admin_password = self.check_pass_length(self.script.get("django_admin_password"))
            self.user_uuid = self.script.get("okeanos_user_uuid")
            self.create_permitted_uuids_file(self.user_uuid)
            self.create_encrypt_file(self.user_uuid)
            self.django_secret_key = self.create_secret_key()
            tag = 'postimage'
            vars = '{0} db_password={1} django_admin_password={2} secret_key={3}'.format(vars,self.db_password,
                                                                                         self.django_admin_password,
                                                                                         self.django_secret_key)
 
        ansible_command = 'ansible-playbook -i ansible_hosts staging.yml -e "choose_role=webserver {0}" -t {1}'.format(vars,tag)
        exit_status = subprocess.call(ansible_command, shell=True)
        if exit_status > 0:
            return error_fatal
        logging.log(REPORT, 'Orka server successfully {0}ed.'.format(verb.rstrip('e')))
        if verb == 'update':
            self.action('restart')

 
class OrkaImage(object):
    """
    Class for Orka management image creation
    """

    def __init__(self, opts):
        """Initialization of OrkaImage data attributes"""
        self.opts = opts
        # Master VM ip, placeholder value
        self.server_ip = '127.0.0.1'
        # Instance of an AstakosClient object
        self.auth = check_credentials(self.opts['token'], auth_url)

        # ~okeanos endpoints and user id
        self.endpoints, self.user_id = endpoints_and_user_id(self.auth)

        # Instance of CycladesClient
        self.cyclades = init_cyclades(self.endpoints['cyclades'],self.opts['token'])
        # Instance of CycladesNetworkClient
        self.net_client = init_cyclades_netclient(self.endpoints['network'],self.opts['token'])
        # Instance of Plankton/ImageClient
        self.plankton = init_plankton(self.endpoints['plankton'],self.opts['token'])
        
        self.escience_repo = self.opts['git_repo']
        self.escience_version = self.opts['git_repo_version']
        self.server_name = self.opts['name']
        self.flavor_id = self.opts['flavor_id']
        self.image_id = self.opts['image_id']
        self.project_id = self.opts['project_id']
        
        
    def create_ansible_hosts(self):
        """
        Function that creates the ansible_hosts file and
        returns the name of the file.
        """
        hosts_filename = os.getcwd() + '/ansible_hosts'
        host = '[webserver]'
        with open(hosts_filename, 'w+') as target:
            target.write(host + '\n')
            target.write(self.server['SNF:fqdn'])
            target.write(' ansible_ssh_host=' + self.server_ip + '\n')
        return hosts_filename
        
        
    def create(self):
        """
        Create Orka image
        """
        ssh_pub_path = join(expanduser('~'), ".ssh/id_rsa.pub")
        vars = 'escience_repo={0} escience_version={1}'.format(self.escience_repo,self.escience_version) 
        self.server = self.cyclades.create_server(self.server_name, self.flavor_id, self.image_id,
                                                  personality=personality(ssh_pub_path),
                                                  project_id=self.project_id)
        logging.log(REPORT,' Creating ~okeanos VM...')
        server_pass = self.server['adminPass']
        new_status = self.cyclades.wait_server(self.server['id'], max_wait=MAX_WAIT)
        
        if new_status == 'ACTIVE':
            server_details = self.cyclades.get_server_details(self.server['id'])
            for attachment in server_details['attachments']:
                if attachment['OS-EXT-IPS:type'] == 'floating':
                        self.server_ip = attachment['ipv4']
        sleep(120) # For VM to be pingable
        logging.log(REPORT," ~okeanos VM created, installing python...")
        subprocess.call("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@{0} 'apt-get update && apt-get -y upgrade; apt-get install -y python;'".format(self.server_ip),shell=True)
        self.create_ansible_hosts()
        logging.log(REPORT, " Starting software installations")
        subprocess.call('ansible-playbook -i ansible_hosts staging.yml -e "choose_role=webserver create_orka_admin=True {0}" -t preimage'.format(vars), shell=True)
        logging.log(REPORT, "Root password of server with public ip {0} is: {1}".format(self.server_ip, server_pass))
        
def main():
    """
    Entry point of deploy/create/update/restart orka server utility script.
    """
    orka_parser = ArgumentParser(description='Create an orka management image or start a server created by an ~okeanos orka management image')
    checker = _logger()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                                level=checker.logging_levels[default_logging],
                                datefmt='%Y-%m-%d %H:%M:%S')
    orka_subparsers = orka_parser.add_subparsers(help='Create orka management image or start orka management server')
    parser_create = orka_subparsers.add_parser('create',
                                     help='Create an Orka management image'
                                   ' on ~okeanos.')
    
    parser_common = ArgumentParser(add_help=False)
    parser_common.add_argument('file', type=checker.valid_file_is, 
                                  help='A file containing sensitive info (e.g. passwords).')
    parser_start = orka_subparsers.add_parser('start', parents=[parser_common], help='Start orka server. User must provide a yaml file with the correct properties')
    
    parser_update = orka_subparsers.add_parser('update', parents=[parser_common], help='Update orka server. User must provide a yaml file with the correct properties')
    
    parser_restart = orka_subparsers.add_parser('restart', parents=[parser_common], help='Restart orka server. User must provide a yaml file with the correct properties')
    
    if len(argv) > 1:
        
        parser_create.add_argument("--name", help='Name of VM to be created. Default is orka_server',default="orka_server")
        parser_create.add_argument("--flavor_id", help='Flavor id of VM to be created. Default is 145. Use "kamaki flavor list" for more flavors',
                              default=145)
        parser_create.add_argument("--project_id", help='~okeanos project uuid. Use "kamaki project list" for existing projects',required=True)
        parser_create.add_argument("--image_id", help='OS for the VM. Use "kamaki image list" for existing images.',required=True)       
        parser_create.add_argument("--git_repo", help='git repo to be cloned.Default is grnet/e-science.',
                              default="https://github.com/grnet/e-science.git")
        parser_create.add_argument("--git_repo_version", help='Version/branch of git repo to be cloned.Default is master.',
                              default="master")
        parser_create.add_argument("--token", help='Authentication token for ~okeanos',required=True)
        

        opts = vars(orka_parser.parse_args(argv[1:]))
        verb = argv[1]  # Main action, decision follows
        try:
            if verb == 'create':
                orka_image = OrkaImage(opts)
                orka_image.create()
            else:         
                orka_server = OrkaServer(opts)
                orka_server.action(verb)
        except Exception, e:
            logging.error('{0} action failed due to {1}'.format(verb,e.args[0]))

    else:
        logging.error('No arguments were given')
        orka_parser.parse_args(' -h'.split())
        exit(error_fatal)
         

if __name__ == "__main__":
    main()
