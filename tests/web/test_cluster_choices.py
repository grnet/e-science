#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the message in summary screen that user's cluster
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
        driver.find_element_by_id("master").click()
        Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text("3")
        time.sleep(1)
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
                if "Everything is ok with your cluster creation parameters" == driver.find_element_by_css_selector("#footer > h4").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        time.sleep(3)
        self.assertEqual("Everything is ok with your cluster creation parameters",
                         driver.find_element_by_css_selector("#footer > h4").text)


if __name__ == "__main__":
    unittest.main()
