#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the network limit error message in summary screen

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from ConfigParser import RawConfigParser, NoSectionError
import unittest, time, re
from okeanos_utils import check_credentials, endpoints_and_user_id, init_cyclades_netclient
import logging
from ClusterTest import ClusterTest

error_quotas_network = -14
error_create_network = -29

BASE_DIR = join(dirname(abspath(__file__)), "../..")


class TestClusterNetwork(ClusterTest):

    def test_cluster(self):

        driver = self.login()
        Select(driver.find_element_by_xpath("//div[@id='sidebar']/p/select")).select_by_visible_text("3")
        time.sleep(1)
        try:
            net_client, net_ids = self.bind_okeanos_resources()
            driver.find_element_by_css_selector("#content-wrap > p > button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button").click()
            time.sleep(1)
            driver.find_element_by_id("slaves").click()
            time.sleep(1)
            driver.find_element_by_css_selector("#content-wrap > p > button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/h4[5]/input").clear()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/h4[5]/input").send_keys("mycluster")
            time.sleep(1)
            driver.find_element_by_id("next").click()
            driver.find_element_by_id("next").click()
            for i in range(60):
                try:
                    if "Private Network quota exceeded" == driver.find_element_by_css_selector("#footer > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Private Network quota exceeded", driver.find_element_by_css_selector("#footer > h4").text)
        finally:
            for net_id in net_ids:
                net_client.delete_network(net_id)

    def bind_okeanos_resources(self):

        auth = check_credentials(self.token)
        endpoints, user_id = endpoints_and_user_id(auth)
        net_client=init_cyclades_netclient(endpoints['network'], self.token)
        dict_quotas = auth.get_quotas()
        limit_net = dict_quotas['system']['cyclades.network.private']['limit']
        usage_net = dict_quotas['system']['cyclades.network.private']['usage']
        pending_net = dict_quotas['system']['cyclades.network.private']['pending']
        available_networks = limit_net - usage_net - pending_net
        network_ids =[]
        if available_networks >= 1:
            logging.info(' Private Network quota is ok')
            try:
                for i in range(available_networks):
                    new_network = net_client.create_network('MAC_FILTERED', 'mycluster ' + str(i))
                    network_ids.append(new_network['id'])
                return net_client,network_ids
            except Exception:
                logging.exception('Error in creating network')
                sys.exit(error_create_network)
        else:
            logging.error('Private Network quota exceeded')
            return error_quotas_network


if __name__ == "__main__":
    unittest.main()
