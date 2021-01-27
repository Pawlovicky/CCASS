from selenium import webdriver
import pandas as pd
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options

class GetCCASSData:
    def __init__(self):
        self.code = None
        self.url = 'https://www.hkexnews.hk/sdw/search/searchsdw.aspx'
        self.driver = None
        self.until = None
        # List of stocks to loop over
        self.stocks = None
        # List of date selected
        self.date = None
        # Default Date, which is shown when the webpage is called
        self.defaultdate = None
    
    def start_driver(self):
        # Call this only when starting the browser
        options = Options()
        fn = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
        options = Options()
        #options.binary_location = driverfn
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path=fn, options=options)
        #self.driver = webdriver.Chrome(driverfn)
        self.until = WebDriverWait(self.driver, 20).until
        return self
    
    def get_list_of_stocks_asof(self, dt):
        strdate = dt.strftime('%Y%m%d')
        urltemplate = 'https://www.hkexnews.hk/sdw/search/stocklist.aspx?sortby=stockcode&shareholdingdate={date}'
        url = urltemplate.format(date=strdate)
        stocks = pd.read_html(url)[0]
        stocks.columns = stocks.columns.get_level_values(1)
        self.stocks = stocks
        return self
    
    def goto_searchpage(self):
        self.driver.get(self.url)
        self.wait = WebDriverWait(self.driver, 20)
        self._get_default_date()
        return self
    
    def enter_stock(self, code):
        stockcode = self.driver.find_element_by_name('txtStockCode')
        stockcode.send_keys(str(code).zfill(5))
        return self
    
    def _get_default_date(self):
        curdate = self.driver.find_element_by_name('txtShareholdingDate').get_attribute('value')
        curdate = pd.Timestamp(curdate)
        self.defaultdate = curdate
        return self
    
    def get_current_date(self):
        curdate = self.driver.find_element_by_name('txtShareholdingDate').get_attribute('value')
        curdate = pd.Timestamp(curdate)
        return curdate
    
    def click_date(self, dt):
        date = self.driver.find_element_by_name('txtShareholdingDate')
        date.click()
        dstr = "//*[@id='date-picker']/div[1]/b[3]/ul/li[{day}]/button"
        mstr = '//*[@id="date-picker"]/div[1]/b[2]/ul/li[{month}]/button'
        ystr = '//*[@id="date-picker"]/div[1]/b[1]/ul/li[{yearidx}]/button'
        if dt.year == self.defaultdate.year:
            yearidx = 1
        if dt.year < self.defaultdate.year:
            yearidx = 2
        self.driver.find_element(By.XPATH, ystr.format(yearidx = yearidx)).click()
        self.driver.find_element(By.XPATH, mstr.format(month = dt.month)).click()
        day = self.driver.find_element(By.XPATH, dstr.format(day = dt.day))
        webdriver.ActionChains(self.driver).double_click(day).perform()
        return self
    
    def click_search_button(self):
        self.driver.find_element(By.ID, 'btnSearch').click()
        self.until(lambda x:x.find_element(By.TAG_NAME, 'table'))
        
    def quit(self):
        self.driver.quit()
    
    def read_main_table(self):
        df = pd.read_html(self.driver.page_source)[-1]
        for col in df.columns:
            df.loc[:, col] = df[col].astype(str).str.split(':', n=1).str.get(1)\
                                    .str.strip()
        return df
    
    def __enter__(self):
        self.start_driver().goto_searchpage()
        return self
    
    def __exit__(self, type, value, traceback):
        self.quit()
    