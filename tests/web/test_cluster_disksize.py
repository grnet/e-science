#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the disk_size limit error message in cluster/create screen

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
import os
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest, time, re
from okeanos_utils import check_quota, get_flavor_id, destroy_cluster
from create_cluster import YarnCluster
from ClusterTest import ClusterTest


class TestClusterDiskSize(ClusterTest):
    '''Test Class for the disk_size limit error message'''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token, self.project_id)
        flavors = get_flavor_id(self.token)
        # List of disk size choices
        disk_list = flavors['disk']
        # Avalable user disk size
        available_disk = user_quota['disk']['available']
        # Give Selenium the values cluster_size, master and slave to use for
        # the cluster_size, master and slave disksize buttons of 
        # cluster/create screen.
        cluster_size, master, slave ,remaining_disk = self.calculate_cluster_resources(disk_list, available_disk)
        
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text(str(cluster_size))
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')
        time.sleep(1)
        driver.find_element_by_id("cluster_name").clear()
        driver.find_element_by_id("cluster_name").send_keys("mycluster")
        try:
            # Call the bind function that creates ~okeanos vms and 
            # causes later the server to respond with an error message to
            # user's create cluster request
            master_ip, server = self.bind_okeanos_resources(remaining_disk, disk_list)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div[2]/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div[3]/div/button["+ master +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div[2]/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div[3]/div/button["+ slave +"]").click()
            time.sleep(1)
            driver.find_element_by_id("next").click()
            for i in range(60):
                try:
                    if "Disk size selection exceeded cyclades disk size limit" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Disk size selection exceeded cyclades disk size limit",
                             driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)
        finally:
            os.system('rm *_root_password')
            destroy_cluster(self.token, master_ip)

    def bind_okeanos_resources(self, remaining_disk, disk_list):
        '''
        Create a bare cluster in ~okeanos with two vms. The disk size depend
        on remaining_disk argument.
        '''
        if remaining_disk == 0:
	    opts = {"name": self.name,
                              "clustersize": 2,
                              "cpu_master": 1, "ram_master": 1024, "disk_master": 5,
                              "disk_template":'ext_vlmc', "cpu_slave": 1,
                              "ram_slave": 1024, "disk_slave": 5, "token": self.token,
                              "image": 'Debian Base', "project_name": self.project_name}
	    c_yarn_cluster = YarnCluster(opts)
            return c_yarn_cluster.create_bare_cluster()
  
        else:
            for disk in disk_list:
                if disk >= remaining_disk:
                    remaining_disk = disk
                    opts = {"name": self.name,
                              "clustersize": 2,
                              "cpu_master": 1, "ram_master": 1024, "disk_master": remaining_disk,
                              "disk_template":'ext_vlmc', "cpu_slave": 1,
                              "ram_slave": 1024, "disk_slave": remaining_disk, "token": self.token,
                              "image": 'Debian Base', "project_name": self.project_name}
	            c_yarn_cluster = YarnCluster(opts)
                    return c_yarn_cluster.create_bare_cluster()

if __name__ == "__main__":
    unittest.main()
