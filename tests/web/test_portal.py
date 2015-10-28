# -*- coding: utf-8 -*-

'''
This script tests portal homepage is active using selenium

@author: eScience Dev-Team
'''

import unittest
from selenium import webdriver
from os import environ

class PortalTest(unittest.TestCase):
    def setUp(self):
        if ("TRAVIS" in environ) or ("CONTINUOUS_INTEGRATION" in environ):
            print "on Travis CI"
            self.driver = webdriver.PhantomJS('phantomjs')
        else:
            print "locally"
            self.driver = webdriver.Firefox()
    
    def test_homepage(self):
        '''
        Open orka portal homepage and check rendering 
        '''
        driver = self.driver
        # open base url and check title
        driver.get("http://localhost:8000/")
        print driver.get_element_by_id('summary').text
        self.assertIn('GRNET e-Science', driver.title)
        
        # find the welcome text to verify the page has rendered
        self.assertTrue(driver.find_element_by_class_name('h2').is_displayed())
        self.assertIn('Welcome to ORKA!',driver.find_element_by_class_name('h2').text)
    
    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
