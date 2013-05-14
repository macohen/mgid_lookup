from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, sys

class MgidChecker2(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "https://mrm.freewheel.tv/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.mgid_list = []
        self.read_mgids("mgids.txt")
        self.login()

    def read_mgids(self, filename):
        mgid_file = open(filename, 'rb')
        for line in mgid_file.readlines():
            self.mgid_list.append(line.strip())
        mgid_file.close()

    def login(self):
        self.username = raw_input("Enter MRM Login: ")
        import getpass
        self.password = getpass.getpass("Password: ", sys.stderr)
        
    def test_mgid_checker2(self):
        driver = self.driver
        driver.get(self.base_url + "/system/account/login?sso_return_to=https%3A%2F%2Fmrm.freewheel.tv%2F&source=MRM")
        driver.find_element_by_name("login").send_keys(self.username)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_css_selector("button.ghBtn").click()
        driver.find_element_by_xpath("//ul[@id='tabs']/li[5]/a/span").click()
        for mgid in self.mgid_list:
            driver.find_element_by_id("query").click()
            driver.find_element_by_id("query").clear()
            driver.find_element_by_id("query").send_keys(mgid)
            driver.find_element_by_id("topnav_search_submit").click()
            elements = driver.find_elements_by_xpath("//tr[starts-with(@id,'asset_')]")
            if elements == None or len(elements) == 0:
                print mgid + " not found in MRM"
            else:
                for elem in elements:
                    print mgid +"=" + elem.text
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
