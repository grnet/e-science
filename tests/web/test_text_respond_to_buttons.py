# -*- coding: utf-8 -*-
'''
This script is a test generator and checks that the summary of each flavors responds when the coresponding buttons are pressed

@author: Ioannis Stenos, Nick Vrionis
'''
from selenium import webdriver
import sys, os
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../../orka-0.1.1/orka'))
sys.path.append(join(dirname(__file__), '../../ember_django/backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from ConfigParser import RawConfigParser, NoSectionError
from okeanos_utils import check_quota, get_flavor_id, check_credentials
import unittest, time, re

BASE_DIR = join(dirname(abspath(__file__)), "../..")

class test_text_respond_to_buttons(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
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
        except NoSectionError:
            self.token = 'INVALID_TOKEN'
            self.auth_url = "INVALID_AUTH_URL"
            self.base_url = "INVALID_APP_URL"
            print 'Current authentication details are kept off source control. ' \
                  '\nUpdate your .config.txt file in <projectroot>/.private/'
    
    def test_text_respond_to_buttons(self):
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
        driver.find_element_by_id("id_services_dd").click()
        driver.find_element_by_id("id_create_cluster").click()        
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id_title_cluster_create_route"))
            ) 
        except: self.fail("time out")
        auth = check_credentials(self.token)
        try:
            list_of_projects = auth.get_projects(state='active')
        except Exception:
            self.assertTrue(False,'Could not get list of projects')
        kamaki_flavors = get_flavor_id(self.token)
        for project in list_of_projects:            
            user_quota = check_quota(self.token, project['id']) 
            if project['name'] == 'system:' + project['id']:
                project_name = 'system'
            else:
                project_name = project['name']               
            project_details = project_name + '        ' + 'VMs:' + str(user_quota['cluster_size']['available']) + '  ' + 'CPUs:' + str(user_quota['cpus']['available']) + '  ' + 'RAM:' + str(user_quota['ram']['available']) + 'MB' + '  ' + 'Disk:' + str(user_quota['disk']['available']) + 'GB'                            
            Select(driver.find_element_by_id("project_id")).select_by_visible_text(project_details)
            cluster_sizes = driver.find_element_by_id("size_of_cluster").text
            try:
                current_cluster_size = int(cluster_sizes.rsplit('\n', 1)[-1])
                print ('Project '+ project_name +' has enough vms to run the test')
                if ((user_quota['cpus']['available']-2*kamaki_flavors['cpus'][0]) >= 0):          
                    driver.find_element_by_id("master_cpus_" + str(kamaki_flavors['cpus'][0])).click()
                    try: self.assertEqual("CPUs: {0}".format(str(kamaki_flavors['cpus'][0])), driver.find_element_by_id("master_cpu_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))       
        
                    driver.find_element_by_id("slaves_cpus_" + str(kamaki_flavors['cpus'][0])).click() 
                    try: self.assertEqual("CPUs each: {0}".format(str(kamaki_flavors['cpus'][0])), driver.find_element_by_id("slaves_cpu_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))
                else:
                    self.assertTrue(False,'Not enought cpu to run the test')
                if ((user_quota['ram']['available']-2*kamaki_flavors['ram'][0]) >= 0):
                    driver.find_element_by_id("master_ram_" + str(kamaki_flavors['ram'][0])).click()       
                    try: self.assertEqual("RAM: {0}".format(str(kamaki_flavors['ram'][0])), driver.find_element_by_id("master_ram_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))
                    driver.find_element_by_id("slaves_ram_" + str(kamaki_flavors['ram'][0])).click()
                    try: self.assertEqual("RAM each: {0}".format(str(kamaki_flavors['ram'][0])), driver.find_element_by_id("slaves_ram_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))
                else:
                    self.assertTrue(False,'Not enought ram to run the test')
                if ((user_quota['disk']['available']-2*kamaki_flavors['disk'][0]) >= 0):
                    driver.find_element_by_id("master_disk_" + str(kamaki_flavors['disk'][0])).click()       
                    try: self.assertEqual("Disk Size: {0}".format(str(kamaki_flavors['disk'][0])), driver.find_element_by_id("master_disk_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))
                    driver.find_element_by_id("slaves_disk_" + str(kamaki_flavors['disk'][0])).click()   
                    try: self.assertEqual("Disk Size each: {0}".format(str(kamaki_flavors['disk'][0])), driver.find_element_by_id("slaves_disk_summary").text)
                    except AssertionError as e: self.verificationErrors.append(str(e))
                else:
                    self.assertTrue(False,'Not enought disk to run the test')
            except:
                #   self.assertTrue(False,'Not enought vms to run the test')
                print ('Project '+ project_name +' has not enough vms to run the test') 



    
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
