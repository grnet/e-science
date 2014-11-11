#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script tests invalid token input using selenium

@author: Ioannis Stenos, Nick Vrionis
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from ClusterTest import ClusterTest

# Constants
num_of_attempts = 60 # delay until token is acknowledge as wrong
token = "invalid" # a invalid okeanos token

class InvalidTokenTest(ClusterTest):

    def test_invalid_token(self):
        '''
        InvalidTokenTest
        Opens homepage then enters login screen 
        and place an invalid okeanos token
        checks if alert message appears 
        '''
        driver = self.driver
        driver.get(self.base_url + "#/homepage")
        driver.find_element_by_css_selector("button[type=\"submit\"]").click()
        driver.find_element_by_id("token").clear()
        driver.find_element_by_id("token").send_keys(token)
        driver.find_element_by_css_selector("button[type=\"login\"]").click()
        for i in range(num_of_attempts):
            try:
                if "Wrong Token. Please try again" == driver.find_element_by_css_selector("div.alert").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertEqual("Wrong Token. Please try again", driver.find_element_by_css_selector("div.alert").text)
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()