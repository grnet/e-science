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
from okeanos_utils import check_quota, get_flavor_id
from create_bare_cluster import create_cluster

BASE_DIR = join(dirname(abspath(__file__)), "../..")


class TestClusterSize(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        self.name = 'testcluster'
        parser.read(config_file)
        try:
            self.token = parser.get('cloud \"~okeanos\"', 'token')
            self.auth_url = parser.get('cloud \"~okeanos\"', 'url')
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

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
        # Get user quota from kamaki
        user_quota = check_quota(self.token)
        # Maximum available clustersize
        max_vms = str(user_quota['cluster_size']['available'])
        # Tell selenium to get the max available clustersize from dropdown
        Select(driver.find_element_by_xpath("//div[@id='sidebar']/p/select")).select_by_visible_text(max_vms)
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
        for i in range(60):
            try:
                if "Selected cluster size exceeded cyclades virtual machines limit" == driver.find_element_by_css_selector("#footer > h4").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        time.sleep(3)
        self.assertEqual("Selected cluster size exceeded cyclades virtual machines limit", driver.find_element_by_css_selector("#footer > h4").text)
        
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    # create a bare cluster with two vms, so we can
    # bind the resources  
    def bind_okeanos_resources(self):

        create_cluster(name=self.name,
                       clustersize=2,
                       cpu_master=1, ram_master=1024, disk_master=5,
                       disk_template='ext_vlmc', cpu_slave=1, ram_slave=1024,
                       disk_slave=5, token=self.token,
                       image='Debian Base')

if __name__ == "__main__":
    unittest.main()