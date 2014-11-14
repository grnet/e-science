#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the cpu limit error message in summary screen

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


class TestClusterCpu(ClusterTest):
    '''Test Class for the cpu limit error message '''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token)
        flavors = get_flavor_id(self.token)
        # List of cpu choices
        cpu_list = flavors['cpus']
        # Avalable user cpu
        available_cpu = user_quota['cpus']['available']
        cluster_size, master, slave, remaining_cpu= self.calculate_cluster_resources(cpu_list, available_cpu)

        # Give Selenium the values cluster_size, master and slave to use for
        # the cluster_size and cpus buttons of cluster/create screen.
        driver.find_element_by_id("master").click()
        Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text(str(cluster_size))
        time.sleep(1)
        try:
            master_ip, server = self.bind_okeanos_resources(remaining_cpu, cpu_list)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button["+ master +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button").click()
            time.sleep(1)
            driver.find_element_by_id("slaves").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button["+ slave +"]").click()
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
                    if "Cpu selection exceeded cyclades cpu limit" == driver.find_element_by_css_selector("#footer > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Cpu selection exceeded cyclades cpu limit",
                             driver.find_element_by_css_selector("#footer > h4").text)
        finally:
            cluster_name = server[0]['name'].rsplit('-', 1)[0]
            destroy_cluster(cluster_name, self.token)

    def bind_okeanos_resources(self, remaining_cpu, cpu_list):
        '''
        Create a bare cluster in ~okeanos with two vms. The cpus depend
        on remaining_cpu argument.
        '''
        if remaining_cpu == 0:
            return create_cluster(name=self.name,
                                  clustersize=2,
                                  cpu_master=1, ram_master=1024, disk_master=5,
                                  disk_template='ext_vlmc', cpu_slave=1,
                                  ram_slave=1024, disk_slave=5,
                                  token=self.token, image='Debian Base')
        else:
            for cpu in cpu_list:
                if cpu >= remaining_cpu:
                    remaining_cpu = cpu
                    return create_cluster(name=self.name,
                                          clustersize=2,
                                          cpu_master=remaining_cpu, ram_master=1024,
                                          disk_master=5, disk_template='ext_vlmc',
                                          cpu_slave=remaining_cpu, ram_slave=1024,
                                          disk_slave=5, token=self.token,
                                          image='Debian Base')

if __name__ == "__main__":
    unittest.main()
