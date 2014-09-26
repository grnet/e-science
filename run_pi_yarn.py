#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script checks a yarn cluster and run a pi job in ~okeanos.

@author: Ioannis Stenos, Nick Vrionis
'''

FILE_RUN_PI = '/home/developer/e-science/temp_file.txt'  # File used from pi function to write stdout

from ansible_create_yarn_cluster import *


def check_string(to_check_file, to_find_str):
    '''
    Search the string passed as argument in the to_check file.
    If string is found, returns the whole line where the string was
    found. Function is used by the run_pi_yarn function.
    '''
    with open(to_check_file, 'r') as f:
        found = False
        for line in f:
            if re.search(to_find_str, line):
                return line
        if not found:
            logging.warning('The line %s cannot be found!', to_find_str)


def run_pi_yarn(name, pi_map=2, pi_sec=10000):
    '''Runs a pi job'''
    #hduser_pass = get_hduser_pass()
    ssh_client = establish_connect(name, 'hduser', '',
                                   MASTER_SSH_PORT)

    logging.log(REPORT, ' Running pi job')
    command = '/usr/local/hadoop/bin/hadoop jar' \
              ' /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.5.1.jar pi ' + \
              str(pi_map)+' '+str(pi_sec)
    exec_command_yarn(ssh_client, command)
    line = check_string(FILE_RUN_PI, "Estimated value of Pi is")
    os.system('rm ' + FILE_RUN_PI)
    ssh_client.close()
    return float(line[25:])


def test_run_pi():
    '''
    Test that runs two pi jobs with different arguments on
    an existing yarn cluster.
    '''
    name = 'xxxx'
    assert run_pi_yarn(name, 2, 10000) == 3.14280000000000000000
    assert run_pi_yarn(name, 10, 1000000) == 3.14158440000000000000


def test_create_cluster_run_pi():
    '''
    Test that calls create_cluster and then tests run_pi_yarn. Function is
    called with different first argument the second time.
    '''
    os.system('kamaki user authenticate > ' + FILE_KAMAKI)
    output = subprocess.check_output("awk '/expires/{getline; print}' "
                                     + FILE_KAMAKI, shell=True)
    token = output.replace(" ", "")[3:-1]
    os.system('rm ' + FILE_KAMAKI)
    name = create_cluster('yarn', 4, 4, 4096, 20,
                          'ext_vlmc', 4, 4096, 20, token,
                          'Debian Base')
    assert run_pi_yarn(name, 2, 100000) == 3.14118000000000000000

    assert run_pi_yarn(name, 10, 100000) == 3.14155200000000000000

def main(opts):
    '''
    The main function calls run_pi_yarn with
    arguments given in command line.
    '''
    pi_value = run_pi_yarn(opts.name, opts.pi_first, opts.pi_second)
    logging.log(REPORT, 'Pi value for arguments %d and %d is %f',
                opts.pi_first, opts.pi_second, pi_value)


if __name__ == '__main__':

    kw = {}
    kw['usage'] = '%prog [options]'
    kw['description'] = '%prog checks a yarn cluster and runs a pi job on' \
                        'Synnefo w. kamaki'

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option('--name',
                      action='store', type='string', dest='name',
                      metavar="MASTER NODE NAME",
                      help='The fully qualified domain name of master node')
    parser.add_option('--pi_first',
                      action='store', type='int', dest='pi_first',
                      metavar='PI FIRST ARG',
                      help='pi job first argument.Default is 2',
                      default=2)
    parser.add_option('--pi_second',
                      action='store', type='int', dest='pi_second',
                      metavar='PI SECOND ARG',
                      help='pi job second argument.Defaut is 10000',
                      default=10000)

    opts, args = parser.parse_args(argv[1:])
    logging.addLevelName(REPORT, "REPORT")
    logger = logging.getLogger("report")

    logging_level = REPORT
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging_level, datefmt='%H:%M:%S')
    main(opts)
