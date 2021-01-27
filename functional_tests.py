from CCASS_SCRAPER.GetCCASSData import GetCCASSData
from CCASS_SCRAPER.CCASSDownloadManager import CCASSDownloadManager
from CCASS_SCRAPER import run_ccass as rc
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

class CCASSDownloadManagerTest(unittest.TestCase):
    def setUp(self):
        self.cdl = CCASSDownloadManager().load().filter_tasks()
        return self
    
    def test_downloads(self):
        selcodes = [175]
        sdf = self.cdl.taskdf.loc[self.cdl.taskdf['code'].isin(selcodes)]
        rlist = sdf.sample(frac=0.1, random_state=1).set_index('date')\
                   .loc[:, ['code']].to_records().tolist()
        n = 5
        lofl = [rlist[i::n] for i in range(n)]
        from multiprocessing import Pool
        p = Pool(5)
        dfs = p.map(rc.run_for_all_stocks_by_records, lofl)
        tdf = pd.concat(dfs)
        cond = tdf.loc[tdf['Participant ID'] == 'C00019'].sort_values('date')\
                  .set_index('date')['Shareholding'].iloc[0] == '2,811,634,518'
        self.assertTrue(cond)
        
        
if __name__ == '__main__':  
    unittest.main()