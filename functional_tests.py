from CCASS_SCRAPER.GetCCASSData import GetCCASSData
from CCASS_SCRAPER.CCASSDownloadManager import CCASSDownloadManager
from CCASS_SCRAPER import run_ccass as rc
from CCASS_SCRAPER.TestData import get_holdings_test_data
from selenium import webdriver
import pandas as pd
import os

import unittest
class GetCCASSDataTest(unittest.TestCase):
    
    def setUp(self):
        self.gcas = GetCCASSData().start_driver().goto_searchpage()
    
    def tearDown(self):
        self.gcas.quit()
    
    def test_click_date(self):
        dt = self.gcas.get_current_date()
        rdt = self.gcas.click_date(dt).get_current_date()
        self.assertEqual(dt, rdt)
    
    def test_read_main_table(self):
        code = 1
        self.gcas.enter_stock(code)
        self.gcas.click_date(self.gcas.defaultdate)
        self.gcas.click_search_button()
        df = self.gcas.read_main_table()
        self.assertTrue(df.shape[0] > 0)

class TestDataTester(unittest.TestCase):
    
    def test_data_generator(self):
        startdate = pd.Timestamp('2020-10-01')
        enddate = pd.Timestamp('2021-01-28')
        df = get_holdings_test_data(startdate, enddate, 1)
        self.assertTrue(df.shape[0] > 0)
        
if __name__ == '__main__':  
    unittest.main()
