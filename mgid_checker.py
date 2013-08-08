from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, sys
from argparse import ArgumentParser

filename = None
class MgidChecker2(unittest.TestCase):
	
    def setUp(self):
        self.first_write = True
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)
        self.base_url = "https://mrm.freewheel.tv/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.mgid_list = []
        self.mgid_dict = {}
        self.read_mgids(filename)
        self.login()

    def read_mgids(self, filename):
        self.in_file = filename
        mgid_file = open(filename, 'rb')
        for line in mgid_file.readlines():
            fields = line.strip().split('\t')
            series_name = ""
            if len(fields) > 1:
                series_name=fields[1]
            mgid = fields[0]
            if mgid.strip() == "":
                continue
            self.mgid_dict[mgid] = series_name
        mgid_file.close()

    def login(self):
        self.username = raw_input("Enter MRM Login: ")
        import getpass
        self.password = getpass.getpass("Password: ", sys.stderr)
        
    def write_file(self, message):
        tsv = None
        if self.first_write == True:
            tsv = open(self.in_file + '_results.tsv','wb')
            tsv.write("mgid\tin_mrm\thas_cuepoints\tmrm_url\n")
            self.first_write = False
        else:
            tsv = open(self.in_file + '_results.tsv','ab')
        tsv.write(message + '\n')
	tsv.close()

    def test_mgid_checker2(self):
        driver = self.driver
        driver.get(self.base_url + "/system/account/login?sso_return_to=https%3A%2F%2Fmrm.freewheel.tv%2F&source=MRM")
        driver.find_element_by_name("login").send_keys(self.username)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_css_selector("button.ghBtn").click()
        driver.find_element_by_xpath("//ul[@id='tabs']/li[5]/a/span").click()
        lookup_results = []
        for mgid,series_name in self.mgid_dict.iteritems():
            retries = 0
            retry = True
            while retry and retries < 3:
                try: 
                    retry = False
                    record = mgid
                    print "checking: " + mgid
                    driver.find_element_by_id("query").click()
                    driver.find_element_by_id("query").clear()
                    driver.find_element_by_id("query").send_keys(mgid)
                    driver.find_element_by_id("topnav_search_submit").click()
                    driver.find_element_by_id("status_filter").click()
                    driver.find_element_by_css_selector("option[value=\"all\"]").click()
                    elements = driver.find_elements_by_xpath("//tr[starts-with(@id,'asset_')]")
                    if elements == None or len(elements) == 0:
                        record += "\tfalse\tfalse"
                        print mgid + ": not found"

                    else:
                        for elem in elements:
                            item_id = elem.get_attribute("item_id")
                            if item_id == None:
                                continue
                            else:
                                record += "\ttrue"
                                print mgid + ":" + item_id
                                item_url = self.base_url + "82125/network/asset/assets/" + item_id
                                driver.get(item_url)
                                src = driver.page_source
                                cue_points = True if src.find("MIDROLL") >= 0 else False
                                if cue_points:
                                    print mgid + ": found cue points"
                                    record += "\ttrue"
                                else:
                                    print mgid + ": no cue points: "
                                    record += "\tfalse"
                                record += "\t" + item_url
                    self.write_file(record)
                    driver.get("https://mrm.freewheel.tv/82125/network/media/search_asset?search_option=all")
                except:
                    retries += 1
                    retry = True
                    print "retrying " + mgid
                    


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
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="the file containing the mgids to look up",required=True)
    #parser.add_option("-l", "--login", dest="mrm_user", help="your MRM user name")
    args = parser.parse_args()
    filename = args.filename 
    del sys.argv[1:]
    unittest.main()
