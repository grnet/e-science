'''
Created on 22 Jul 2014

@author: developer
'''
import sys
sys.stderr = open('/dev/null')       # Silence silly warnings from paramiko
import paramiko
sys.stderr = sys.__stderr__
from sys import argv
import os

'''
Give master's public ip as an argument to run the script

Vyrona o kodikas den einai telikos kai oute commit ready.
Einai kathara dokimastikos gia na mas steileis feedback.
Pairnei thn public ip tou master kai kanei oi xreiazetai gia na ginei hadoop-ready o master
kai sth synexeia egkathista to hadoop. Tasxolia eginan viastika gia na ginei commit kai tha 
allaxthoun later. Episis tha ginontaikai elegxoi an eginan oi egkatastaseis sosta.
'''


def setup_connect_paramiko(ip_addr):
    '''
    Create ssh connection with master as root
    run apt-get update,install sudo
    call other functions
    disconnect as root
    reconnect as hduser
    '''
    ssh=paramiko.SSHClient()
    #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_addr,username='root')
        print "Successfully connected as root" 
    except:
        print "There was an error connecting as root"
        
    stdin,stdout,stderr=ssh.exec_command('apt-get update;apt-get install sudo',get_pty=True)
    stdin.write('N\n')
    stdin.flush()
    print stdout.read(),stderr.read()
    install_python_and_java(ssh)
    add_hduser_disable_ipv6(ssh)
    stdout.close()
    stdin.close()
    ssh.close()
    connect_as_hduser_conf_ssh(ip_addr)
    
    
def connect_as_hduser_conf_ssh(ip_addr):
    '''
    Connect as hduser to master
    create ssh key
    download hadoop from eu apache mirror
    create hadoop folder in usr/local
    per michael noll instructions
    still needs configuration in .bashrc
    '''
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_addr,username='hduser',password='hduserpass')
        print "success in connection as hduser"
    except:
        print "error connecting as hdser"
    
    stdin,stdout,stderr=ssh.exec_command('ssh-keygen -t rsa -P "" ',get_pty=True)
    stdin.write('\n')
    print stdout.read(),stderr.read()
    stdin.flush()
    stdin,stdout,stderr=ssh.exec_command('cat /home/hduser/.ssh/id_rsa.pub >> /home/hduser/.ssh/authorized_keys',get_pty=True)
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('wget www.eu.apache.org/dist/hadoop/common/stable1/hadoop-1.2.1.tar.gz',get_pty=True)
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('sudo tar -xzf $HOME/hadoop-1.2.1.tar.gz',get_pty=True)
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('sudo mv hadoop-1.2.1 /usr/local/hadoop')
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('cd /usr/local;sudo chown -R hduser:hadoop hadoop')
    print stdout.read(),stderr.read()
    
    stdout.close()
    stdin.close()
    ssh.close()
    

def install_python_and_java(ssh):
    '''
    Install python-software-properties
    and oracle java 7
    '''
    stdin,stdout,stderr=ssh.exec_command('apt-get -y install python-software-properties',get_pty=True)
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee /etc/apt/sources.list.d/webupd8team-java.list;echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list',get_pty=True)
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886;apt-get update;echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections;apt-get -y install oracle-java7-installer',get_pty=True) # removed exit in the end
    print stdout.read(),stderr.read()
    stdin,stdout,stderr=ssh.exec_command('apt-get install oracle-java7-set-default',get_pty=True)      
    print stdout.read(),stderr.read()
        
    stdout.close()
    stdin.close()
    

def add_hduser_disable_ipv6(ssh):
    '''
    Creates hadoop group and hduser and
    gives them passwordless sudo to help with remaining procedure
    Also disables ipv6
    '''
    stdin,stdout,stderr=ssh.exec_command('addgroup hadoop;echo "%hadoop ALL=(ALL) NOPASSWD: ALL " >> /etc/sudoers',get_pty=True)
    print stdout.read()
    stdin,stdout,stderr=ssh.exec_command('adduser hduser --disabled-password --gecos "";adduser hduser hadoop;echo "hduser:hduserpass" | chpasswd',get_pty=True)
    print stdout.read()    
    stdin,stdout,stderr=ssh.exec_command('echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6',get_pty=True)
    print stdout.read()
    stdin,stdout,stderr=ssh.exec_command('echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6',get_pty=True)
    print stdout.read()
     
    stdout.close()
    stdin.close()

# JAVA_HOME=/usr/lib/jvm/java-7-oracle


def main(opts):

    setup_connect_paramiko(opts.ip_addr)
    

if __name__ == '__main__':
    from optparse import OptionParser

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog deploys a compute cluster on Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--ip_addr',
                      action='store', type='string', dest='ip_addr',
                      metavar="Ip address",
                      help='Public ip of master') 

    opts, args = parser.parse_args(argv[1:])
    main(opts)