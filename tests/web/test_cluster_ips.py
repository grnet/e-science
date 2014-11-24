#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the public ips limit error message in cluster/create screen


@author: Ioannis Stenos, Nick Vrionis
'''

import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.support.ui import Select
import unittest, time, re, logging
from kamaki.clients import ClientError
from okeanos_utils import check_credentials, endpoints_and_user_id, init_cyclades_netclient, get_project_id
from ClusterTest import ClusterTest

error_get_ip = -30


class TestClusterIps(ClusterTest):
    '''Test Class for the public ips limit error message'''
    def test_cluster(self):

        driver = self.login()
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text("2")
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')        
        try:
            # Call the bind function that creates and binds ~okeanos ips and 
            # causes later the server to respond with an error message to
            # user's create cluster request
            float_ids, port_ids, net_client = self.bind_okeanos_resources()
            driver.find_element_by_id("cluster_name").clear()
            driver.find_element_by_id("cluster_name").send_keys("mycluster")
            time.sleep(1)
            driver.find_element_by_id("master_cpus_1").click()
            time.sleep(1)
            driver.find_element_by_id("master_ram_512").click()
            time.sleep(1)
            driver.find_element_by_id("master_disk_5").click()
            time.sleep(1)
            driver.find_element_by_id("slaves_cpus_1").click()
            time.sleep(1)
            driver.find_element_by_id("slaves_ram_512").click()
            time.sleep(1)
            driver.find_element_by_id("slaves_disk_5").click()
            time.sleep(1)
            driver.find_element_by_id("next").click()
            for i in range(60):
                try:
                    if "Public ip quota exceeded" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Public ip quota exceeded",
                             driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)
        finally:
            self.release_resources(float_ids, port_ids, net_client)

    def bind_okeanos_resources(self):
        '''
        Create every available public ip for the user running the test, call
        bind_floating_ip to attach the ips and return whatever is needed
        for the selenium test.
        '''
        auth = check_credentials(self.token)
        endpoints, user_id = endpoints_and_user_id(auth)
        net_client = init_cyclades_netclient(endpoints['network'],
                                             self.token)

        dict_quotas = auth.get_quotas()
        # Find and create available public ips
	project_id = get_project_id()
        limit_ips = dict_quotas[project_id]['cyclades.floating_ip']['limit']
        usage_ips = dict_quotas[project_id]['cyclades.floating_ip']['usage']
        pending_ips = dict_quotas[project_id]['cyclades.floating_ip']['pending']
        available_ips = limit_ips - (usage_ips + pending_ips)

        if available_ips > 0:
            for i in range(available_ips):
                # Create all available public ips
                status = self.get_flo_net_id(net_client, project_id)
                if status != 0:
                    logging.error('Error in creating float ip')
                    sys.exit(error_get_ip)
        # Call bind_floating_ip to attach every unused ip
        float_ids, port_ids = self.bind_floating_ip(net_client)
        return float_ids, port_ids, net_client

    def get_flo_net_id(self, net_client, project_id):
        '''
        Gets an Ipv4 floating network id from the list of public networks Ipv4
        '''
        pub_net_list = net_client.list_networks()
        float_net_id = 1
        i = 1
        for lst in pub_net_list:
            if(lst['status'] == 'ACTIVE' and
               lst['name'] == 'Public IPv4 Network'):
                float_net_id = lst['id']
                try:
                    net_client.create_floatingip(float_net_id,
                                                 project_id=project_id)
                    return 0
                except ClientError:
                    if i < len(pub_net_list):
                        i = i+1
                    else:
                        return error_get_ip

    def bind_floating_ip(self, net_client):
        '''
        Binds each unattached public ip to a port without creating new
        virtual machines.
        '''
        float_ids = []
        port_ids = []
        try:
            list_float_ips = net_client.list_floatingips()
        except Exception:
            logging.exception('Error getting list of floating ips')
            sys.exit(error_get_ip)
        # If there are existing floating ips, we check if there is any free or
        # if all of them are attached to a machine
        if len(list_float_ips) != 0:
            for float_ip in list_float_ips:
                if float_ip['instance_id'] is None and float_ip['port_id'] is None:

                    port_details = net_client.create_port(float_ip['floating_network_id'], name='test',
                                                  fixed_ips=[{'ip_address': float_ip['floating_ip_address']}])
                    net_client.wait_port(port_details['id'],
                                         current_status='BUILD')

                    port_ids.append(port_details['id'])
                    float_ids.append({'id': float_ip['id'],
                                      'port_id': port_details['id']})

        return float_ids, port_ids

    def release_resources(self, float_ids, port_ids, net_client):
        '''
        Release the resources binded for the test, meaning delete ports
        and public ips created during the test.
        '''
        for port_id in port_ids:
            for float_id in float_ids:
                if float_id['port_id'] == port_id:
                    net_client.delete_port(port_id)
                    net_client.delete_floatingip(float_id['id'])


if __name__ == "__main__":
    unittest.main()
