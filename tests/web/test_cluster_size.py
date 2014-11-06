#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from okeanos_utils import destroy_cluster
from test_cluster_choices import TestCluster

BASE_DIR = join(dirname(abspath(__file__)), "../..")


class TestClusterSize(TestCluster):

    def test_cluster(self):
        driver = self.driver
        driver.get(self.base_url + "#/homepage")
        driver.find_element_by_css_selector("button[type=\"submit\"]").click()
        driver.find_element_by_id("token").clear()
        driver.find_element_by_id("token").send_keys(self.token)
        driver.find_element_by_css_selector("button[type=\"login\"]").click()
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "CreateHadoopCluster"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("CreateHadoopCluster").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//div[@id='sidebar']/p/select"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        Select(driver.find_element_by_xpath("//div[@id='sidebar']/p/select")).select_by_visible_text("3")
        time.sleep(1)
        self.bind_okeanos_resources()
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
        destroy_cluster(self.name, self.token)
        for i in range(60):
            try:
                if "Selected cluster size exceeded cyclades virtual machines limit" == driver.find_element_by_css_selector("#footer > h4").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        time.sleep(3)
        self.assertEqual("Selected cluster size exceeded cyclades virtual machines limit", driver.find_element_by_css_selector("#footer > h4").text)


if __name__ == "__main__":
    unittest.main()
