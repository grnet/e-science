#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script tests login from web form using selenium

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from os.path import join, dirname
import unittest, time, re, sys
from ClusterTest import ClusterTest


class LoginTest(ClusterTest):
    '''Test class for login functionality '''
    def test_login(self):
        '''
        LoginTest
        Opens homepage then enters login screen 
        and place a valid okeanos token
        checks if it has loged in 
        '''
        driver = self.driver
        driver.get(self.base_url + "#/homepage")
        driver.find_element_by_css_selector("button[type=\"submit\"]").click()
        driver.find_element_by_id("token").clear()
        driver.find_element_by_id("token").send_keys(self.token)
        driver.find_element_by_css_selector("button[type=\"login\"]").click()
        for i in range(60):
            try:
                if "Welcome" == driver.find_element_by_css_selector("h2").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertRegexpMatches(driver.find_element_by_id("user").text, r"User: [0-9]+")
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertRegexpMatches(driver.find_element_by_id("clusters").text, r"Clusters: [0-9]+")
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
