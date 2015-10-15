#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the cluster_size error message in cluster/create screen

@author: Ioannis Stenos, Nick Vrionis
'''

import sys
import os
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest, time, re
from okeanos_utils import check_quota, get_flavor_lists, destroy_cluster
from create_cluster import YarnCluster
from ClusterTest import ClusterTest


class TestClusterSize(ClusterTest):
    '''Test Class for cluster_size error message'''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token, self.project_id)
        # Maximum available clustersize
        max_vms = str(user_quota['cluster_size']['available'])
        # Tell selenium to get the max available clustersize from dropdown
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text(max_vms)
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')
        try:
            # Call the bind function that creates ~okeanos vms and 
            # causes later the server to respond with an error message to
            # user's create cluster request
            master_ip, server = self.bind_okeanos_resources()
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
                    if "Selected cluster size exceeded cyclades virtual machines limit" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Selected cluster size exceeded cyclades"
                             " virtual machines limit",
                             driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)
        finally:
            os.system('rm *_root_password')
            destroy_cluster(self.token, master_ip)

    def bind_okeanos_resources(self):
        '''
        Create a bare cluster with two vms, so we can bind the
        resources in ~okeanos
        '''
	opts = {"name": self.name,
                              "clustersize": 2,
                              "cpu_master": 1, "ram_master": 1024, "disk_master": 5,
                              "disk_template":'Standard', "cpu_slave": 1,
                              "ram_slave": 1024, "disk_slave": 5, "token": self.token,
                              "image": 'Debian Base', "project_name": self.project_name}
	c_yarn_cluster = YarnCluster(opts)
        return c_yarn_cluster.create_bare_cluster()
         

if __name__ == "__main__":
    unittest.main()
