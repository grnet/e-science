#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the memory limit error message in summary screen

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
from okeanos_utils import check_quota, get_flavor_id, destroy_cluster
from create_bare_cluster import create_cluster
from ClusterTest import ClusterTest


class TestClusterMemory(ClusterTest):
    '''Test Class for the memory limit error message'''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token)
        flavors = get_flavor_id(self.token)
        # List of ram choices
        ram_list = flavors['ram']
        # Avalable user ram
        available_ram = user_quota['ram']['available']
        cluster_size, master, slave, remaining_ram = self.calculate_cluster_resources(ram_list, available_ram)

        # Give Selenium the values cluster_size, master and slave to use for
        # the cluster_size and ram buttons of cluster/create screen.
        Select(driver.find_element_by_xpath("//div[@id='sidebar']/p/select")).select_by_visible_text(str(cluster_size))
        time.sleep(1)
        try:
            master_ip, server = self.bind_okeanos_resources(remaining_ram, ram_list)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button["+ master +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button").click()
            time.sleep(1)
            driver.find_element_by_id("slaves").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button["+ slave +"]").click()
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
                    if "Ram selection exceeded cyclades memory limit" == driver.find_element_by_css_selector("#footer > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Ram selection exceeded cyclades memory limit",
                             driver.find_element_by_css_selector("#footer > h4").text)
        finally:
            cluster_name = server[0]['name'].rsplit('-', 1)[0]
            destroy_cluster(cluster_name, self.token)

    def bind_okeanos_resources(self, remaining_ram, ram_list):
        '''
        Create a bare cluster in ~okeanos with two vms. The ram depend
        on remaining_ram argument.
        '''
        if remaining_ram == 0:
            return create_cluster(name=self.name,
                                  clustersize=2,
                                  cpu_master=1, ram_master=1024, disk_master=5,
                                  disk_template='ext_vlmc', cpu_slave=1,
                                  ram_slave=1024, disk_slave=5,
                                  token=self.token, image='Debian Base')
        else:
            for ram in ram_list:
                if ram >= remaining_ram:
                    remaining_ram = ram
                    return create_cluster(name=self.name,
                                          clustersize=2,
                                          cpu_master=1, ram_master=remaining_ram,
                                          disk_master=5, disk_template='ext_vlmc',
                                          cpu_slave=1, ram_slave=remaining_ram,
                                          disk_slave=5, token=self.token,
                                          image='Debian Base')

if __name__ == "__main__":
    unittest.main()
