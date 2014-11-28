# -*- coding: utf-8 -*-
'''
This script tests logout from web form using selenium

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from os.path import join, dirname
from ConfigParser import RawConfigParser, NoSectionError
import unittest, time, re, sys

BASE_DIR = join(dirname(abspath(__file__)), "../..")

class TestLogout(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        parser.read(config_file)
        try:
            self.token = parser.get('cloud \"~okeanos\"', 'token')
            self.auth_url = parser.get('cloud \"~okeanos\"', 'url')
            self.base_url = parser.get('deploy', 'url')
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'
    
    def test_logout(self):
        '''
        LogoutTest
        Opens homepage then enters login screen 
        and place a valid okeanos token
        and then logs out back in homepage 
        '''
        driver = self.driver
        driver.get(self.base_url + "#/homepage")
        driver.find_element_by_id("id_login").click()
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id_title_user_login_route"))
            ) 
        except: self.fail("time out") 
        driver.find_element_by_id("token").clear()
        driver.find_element_by_id("token").send_keys(self.token)               
        driver.find_element_by_xpath("//button[@type='login']").click()
        if (self.is_element_present(By.XPATH, "//div[@id='id_alert_wrongtoken']/strong") == True):
            self.assertTrue(False,'Invalid token')
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id_title_user_welcome_route"))
            ) 
        except: self.fail("time out")
        driver.find_element_by_id("id_login_dd").click()
        driver.find_element_by_id("id_logout").click()
        for i in range(60):
            try:
                if "ORCA" == driver.find_element_by_css_selector("h2").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertEqual("WELCOME TO ORCA!", driver.find_element_by_css_selector("p").text)
        except AssertionError as e: self.verificationErrors.append(str(e))
    
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

if __name__ == "__main__":
    unittest.main()
