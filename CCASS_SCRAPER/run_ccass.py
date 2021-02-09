from CCASS_SCRAPER.GetCCASSData import GetCCASSData
import pandas as pd
import os
from selenium.common.exceptions import ElementNotInteractableException, UnexpectedAlertPresentException

def tbl_post_processing(fun):
    def formatter(*args, **kwargs):
        df = fun(*args, **kwargs)
        if df is None:
            return None
        colnms = ['pid', 'pname', 'address', 'shareholding', 'ownership', 'code',
                  'date']
        df.columns = colnms
        df.loc[:, 'shareholding'] = pd.to_numeric(df['shareholding']\
                                         .str.replace(',',''), errors='coerce')
        df.loc[:, 'ownership'] = pd.to_numeric(df['ownership']\
                                         .str.replace('%', ''), errors='coerce')\
                                               /100
        return df
    return formatter

@tbl_post_processing
def download_single_stock_by_daterange(dts, code):
    dfs = []
    with GetCCASSData() as gcas:
        for dt in dts[::-1]:
            gcas.click_date(dt)
            gcas.enter_stock(code)
            try:
                gcas.click_date(dt)
                gcas.click_search_button()
                df = gcas.read_main_table()
                curdt = gcas.get_current_date()
                df = df.assign(code=str(code), date=curdt)
                dfs.append(df)
            except (ElementNotInteractableException, UnexpectedAlertPresentException):
                print('Failed to retrieve {code} for {date}'.\
                      format(code=str(code), date=dt))
                break
    if len(dfs) > 0:
        df = pd.concat(dfs).drop_duplicates()
        return df
    else:
        return None
    
def download_single_stock(sdate, edate, code):
    dts = pd.bdate_range(sdate, edate)
    dts = dts.union(pd.DatetimeIndex([edate]))
    assert len(dts) > 0
    df = download_single_stock_by_daterange(dts, code)
    
@tbl_post_processing    
def run_for_single_stock_by_date(code, dt):
    with GetCCASSData() as gcas:
        gcas.click_date(dt)
        gcas.enter_stock(code)
        try:
            gcas.click_date(dt)
            gcas.click_search_button()
            df = gcas.read_main_table()
            curdt = gcas.get_current_date()
            df = df.assign(code=str(code), date=curdt)
        except ElementNotInteractableException:
            print('Failed to retrieve {code} for {date}'.\
                  format(code=str(code), date=curdt))
    return df

def run_for_all_stocks_by_date(dt):
    with GetCCASSData() as gcas:
        gcas.click_date(dt)
        gcas.get_list_of_stocks_asof(dt)
        dfs = []
        failed_log = None
        for code in gcas.stocks['Stock Code'].unique()[-10:]:
            gcas.enter_stock(code)
            try:
                gcas.click_date(dt)
                gcas.click_search_button()
                df = gcas.read_main_table()
                curdt = gcas.get_current_date()
                dfs.append(df.assign(code=str(code), date=curdt))
            except ElementNotInteractableException:
                failedinfo = pd.DataFrame([code, dt], index=['code', 'date']).T
                failed_log = pd.concat([failed_log, failedinfo])
        if not failed_log is None:
            fn = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S_%f')
            failed_log.to_csv(os.path.join('logs', fn+'.csv'))
    return dfs

def run_for_all_stocks_by_records(trecord):
    """
    This function receives a list of [r0, r1, r2, ...]
    where ri = ('2021-01-05', 7)    and hence date and ticker
    """
    with GetCCASSData() as gcas:
        dfs = []
        failed_log = None
        for dt, code in trecord:
            dt = pd.Timestamp(dt)
            gcas.enter_stock(code)
            try:
                gcas.click_date(dt)
                gcas.click_search_button()
                df = gcas.read_main_table()
                curdt = gcas.get_current_date()
                dfs.append(df.assign(code=str(code), date=curdt))
            except ElementNotInteractableException:
                failedinfo = pd.DataFrame([code, dt], index=['code', 'date']).T
                failed_log = pd.concat([failed_log, failedinfo])
        if not failed_log is None:
            fn = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S_%f')
            failed_log.to_csv(os.path.join('logs', fn+'.csv'))
    return pd.concat(dfs)

def get_current_date():
    with GetCCASSData() as gcas:
        curdate = gcas.defaultdate
    return curdate
