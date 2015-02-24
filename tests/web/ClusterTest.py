#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unittest class used in Selenium tests. Every test_cluster_* inherits methods
from ClusterTest.

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys, os
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../../ember_django'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from ConfigParser import RawConfigParser, NoSectionError
from backend.okeanos_utils import check_quota, check_credentials
import unittest, time, re

BASE_DIR = join(dirname(abspath(__file__)), "../..")


class ClusterTest(unittest.TestCase):
    '''
    setUp method is common for all test_cluster tests.
    Defines the path to okeanos token and the base url for
    the selenium test.
    '''
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True
        parser = RawConfigParser()
        config_file = join(BASE_DIR, '.private/.config.txt')
        self.name = 'testcluster'
        parser.read(config_file)
        try:
            self.token = parser.get('cloud \"~okeanos\"', 'token')
            self.auth_url = parser.get('cloud \"~okeanos\"', 'url')
            self.base_url = parser.get('deploy', 'url')
            self.project_name = parser.get('project', 'name')
            auth = check_credentials(self.token)
            try:
                list_of_projects = auth.get_projects(state='active')
            except Exception:
                self.assertTrue(False,'Could not get list of projects')
            for project in list_of_projects:
                if project['name'] == self.project_name:
                    self.project_id = project['id']
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            self.project_name = "INVALID_PROJECT_NAME"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'

    def login(self):
        '''Method used for login by all test_cluster tests'''
        driver = self.driver
        driver.get(self.base_url + "#/homepage")       
        driver.find_element_by_id("id_login").click()
        
        
        for i in range(30):
            try:
                if "~Okeanos Token" == driver.find_element_by_css_selector("h2").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
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
        driver.find_element_by_id("id_services_dd").click()
        driver.find_element_by_id("id_create_cluster").click()        
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id_title_cluster_create_route"))
            ) 
        except: self.fail("time out")                 
        user_quota = check_quota(self.token, self.project_id)
        project_details = self.project_name + '        ' + 'VMs:' + str(user_quota['cluster_size']['available']) + '  ' + 'CPUs:' + str(user_quota['cpus']['available']) + '  ' + 'RAM:' + str(user_quota['ram']['available']) + 'MB' + '  ' + 'Disk:' + str(user_quota['disk']['available']) + 'GB'                            
        Select(driver.find_element_by_id("project_id")).select_by_visible_text(project_details)
        return driver

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

    def calculate_cluster_resources(self, resource_list, available_resource):
        '''
        Method used by test_cluster_cpu, test_cluster_memory and
        test_cluster_disk to calculate the resources needed to be binded
        during each test in cluster/create screen. Those resources are
        the buttons pressed by selenium test and are not really binded
        in ~okeanos. The result is that much less real resources are binded
        in ~okeanos for the tests.
        '''
        avail = available_resource
        cluster_size = 0
        vms = []
        # Create a vms list with values the combinations of resource size
        # and number of vms we will bind in selenium with a particular,
        # resource flavor e.g for test_cluster_disk vms = [{100:2}, {80:1}]
        # means 2 vms with 100 disk size each and 1 vm with 80 disk size.
        for resource in reversed(resource_list):
            if (available_resource/resource) >= 1:
                vms.append({resource: available_resource/resource})
                if available_resource%resource ==0:
                    break
                available_resource = available_resource - resource*(available_resource/resource)
        # If the vms list has two or more elements
        if len(vms) >= 2:
            # Find the remaining resource that we will bind in ~okeanos for the test.
            remaining_resource = avail - vms[0].values()[0] *vms[0].keys()[0] - vms[1].values()[0] * vms[1].keys()[0]
            # Calculate the cluster_size we will use as input in selenium
            cluster_size = vms[0].values()[0] + vms[1].values()[0]
            # Select the buttons selenium will press
            # in create_cluster screen
            slave = str(resource_list.index(vms[0].keys()[0]) + 1)
            master = str(resource_list.index(vms[1].keys()[0])+ 1)

        # If the vms list has zero elements
        elif len(vms) == 0:
            raise RuntimeError
        # If the vms list has only one element
        else:
            remaining_resource = 0
            cluster_size = cluster_size + vms[0].values()[0]
            slave = str(resource_list.index(vms[0].keys()[0]) + 1)
            master = str(resource_list.index(vms[0].keys()[0]) + 1)

        return cluster_size, master, slave, remaining_resource
