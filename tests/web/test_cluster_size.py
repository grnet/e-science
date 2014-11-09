#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the cluster_size error message in summary screen

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
from okeanos_utils import check_quota, get_flavor_id, destroy_cluster
from create_bare_cluster import create_cluster
from ClusterTest import ClusterTest

BASE_DIR = join(dirname(abspath(__file__)), "../..")


class TestClusterSize(ClusterTest):

    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token)
        # Maximum available clustersize
        max_vms = str(user_quota['cluster_size']['available'])
        # Tell selenium to get the max available clustersize from dropdown
        Select(driver.find_element_by_xpath("//div[@id='sidebar']/p/select")).select_by_visible_text(max_vms)
        time.sleep(1)
        try:
            master_ip, server = self.bind_okeanos_resources()
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
                    if "Selected cluster size exceeded cyclades virtual machines limit" == driver.find_element_by_css_selector("#footer > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Selected cluster size exceeded cyclades virtual machines limit", driver.find_element_by_css_selector("#footer > h4").text)
        finally:
            cluster_name = server[0]['name'].rsplit('-', 1)[0]
            destroy_cluster(cluster_name, self.token)

    # create a bare cluster with two vms, so we can
    # bind the resources in ~okeanos
    def bind_okeanos_resources(self):

        return create_cluster(name=self.name,
                       clustersize=2,
                       cpu_master=1, ram_master=1024, disk_master=5,
                       disk_template='ext_vlmc', cpu_slave=1, ram_slave=1024,
                       disk_slave=5, token=self.token,
                       image='Debian Base')

if __name__ == "__main__":
    unittest.main()