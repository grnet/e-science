#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the message in cluster/create screen that user's cluster
choices are valid


@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
from os.path import join, dirname, abspath
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest, time, re
from ClusterTest import ClusterTest


class TestClusterChoices(ClusterTest):
    '''
    Test Class for the backend response that user's cluster
    choices are valid
    '''
    def test_cluster(self):

        driver = self.login()
        try:
            Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text("2")
            time.sleep(1)
        except:
            self.assertTrue(False,'Not enough vms to run the test')        
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
                if "Everything is ok with your cluster creation parameters" == driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        time.sleep(3)
        self.assertEqual("Everything is ok with your cluster creation parameters",
                        driver.find_element_by_css_selector("div.col.col-sm-6 > h4").text)


if __name__ == "__main__":
    unittest.main()
