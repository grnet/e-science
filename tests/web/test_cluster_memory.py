#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the memory limit error message in cluster/create screen

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
from random import randint


class TestClusterMemory(ClusterTest):
    '''Test Class for the memory limit error message'''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token, self.project_id)
        flavors = get_flavor_id(self.token)
        # List of ram choices
        ram_list = flavors['ram']
        # Avalable user ram
        available_ram = user_quota['ram']['available']
        # Give Selenium the values cluster_size, master and slave to use for
        # the cluster_size, master and slave ram buttons of
        # cluster/create screen.
        cluster_size, master, slave, remaining_ram = self.calculate_cluster_resources(ram_list, available_ram)
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text(str(cluster_size))
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')
        
        time.sleep(1)
        driver.find_element_by_id("cluster_name").clear()
        cluster_name = 'test_cluster' + str(randint(0,9999))
        driver.find_element_by_id("cluster_name").send_keys(cluster_name)
        try:
            # Call the bind function that creates ~okeanos vms and 
            # causes later the server to respond with an error message to
            # user's create cluster request
            master_ip, server = self.bind_okeanos_resources(remaining_ram, ram_list)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div[2]/div/button["+ master +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[4]/div[2]/div/div[3]/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div/div/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div[2]/div/button["+ slave +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='wrap']/div[2]/div/div/div[5]/div[2]/div/div[3]/div/button").click()
            time.sleep(1)
            driver.find_element_by_id("next").click()
            for i in range(60):
                try:
                    if "Ram selection exceeded cyclades memory limit" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Ram selection exceeded cyclades memory limit",
                             driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)
        finally:
            os.system('rm *_root_password')
            destroy_cluster(self.token, master_ip)

    def bind_okeanos_resources(self, remaining_ram, ram_list):
        '''
        Create a bare cluster in ~okeanos with two vms. The ram depend
        on remaining_ram argument.
        '''
        if remaining_ram == 0:
	    opts = {"name": self.name,
                              "clustersize": 2,
                              "cpu_master": 1, "ram_master": 1024, "disk_master": 5,
                              "disk_template":'Archipelago', "cpu_slave": 1,
                              "ram_slave": 1024, "disk_slave": 5, "token": self.token,
                              "image": 'Debian Base', "project_name": self.project_name}
	    c_yarn_cluster = YarnCluster(opts)
            return c_yarn_cluster.create_bare_cluster()

        else:
            for ram in ram_list:
                if ram >= remaining_ram:
                    remaining_ram = ram
                    opts = {"name": self.name,
                              "clustersize": 2,
                              "cpu_master": 1, "ram_master": remaining_ram, "disk_master": 5,
                              "disk_template":'Archipelago', "cpu_slave": 1,
                              "ram_slave": remaining_ram, "disk_slave": 5, "token": self.token,
                              "image": 'Debian Base', "project_name": self.project_name}
	            c_yarn_cluster = YarnCluster(opts)
                    return c_yarn_cluster.create_bare_cluster()

if __name__ == "__main__":
    unittest.main()
