#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the network limit error message in cluster/create screen

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest, time, re
from okeanos_utils import check_credentials, endpoints_and_user_id, init_cyclades_netclient, get_project_id
import logging
from ClusterTest import ClusterTest

error_quotas_network = -14
error_create_network = -29


class TestClusterNetwork(ClusterTest):
    '''Test Class for the network limit error message'''
    def test_cluster(self):

        driver = self.login()
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text("2")
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')
        
        try:
            # Call the bind function that creates ~okeanos private networks
            # and causes later the server to respond with an error message to
            # user's create cluster request
            net_client, net_ids = self.bind_okeanos_resources()
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
                    if "Private Network quota exceeded" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Private Network quota exceeded",
                             driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)
        finally:
            for net_id in net_ids:
                net_client.delete_network(net_id)

    def bind_okeanos_resources(self):
        '''
        Binds all available private networks in ~okeanos
        for the user running the test.
        '''
        auth = check_credentials(self.token)
        endpoints, user_id = endpoints_and_user_id(auth)
        net_client = init_cyclades_netclient(endpoints['network'], self.token)
        dict_quotas = auth.get_quotas()
        project_id = get_project_id()
        limit_net = dict_quotas[project_id]['cyclades.network.private']['limit']
        usage_net = dict_quotas[project_id]['cyclades.network.private']['usage']
        pending_net = dict_quotas[project_id]['cyclades.network.private']['pending']
        available_networks = limit_net - usage_net - pending_net
        network_ids = []
        if available_networks >= 1:
            logging.info(' Private Network quota is ok')
            try:
                for i in range(available_networks):
                    new_network = net_client.create_network('MAC_FILTERED',
                                                            'mycluster '
                                                            + str(i),
                                                            project_id=project_id)
                    network_ids.append(new_network['id'])
                return net_client, network_ids
            except Exception:
                logging.exception('Error in creating network')
                sys.exit(error_create_network)
        else:
            logging.error('Private Network quota exceeded')
            return error_quotas_network


if __name__ == "__main__":
    unittest.main()
