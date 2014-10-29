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

# Constants
num_of_attempts = 60 # delay until token is acknowledge as wrong
token = "invalid" # a invalid okeanos token

class InvalidTokenTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://83.212.123.218:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
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
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to.alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert()
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

if __name__ == "__main__":
    unittest.main()
