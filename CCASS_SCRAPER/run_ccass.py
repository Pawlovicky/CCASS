from CCASS_SCRAPER.GetCCASSData import GetCCASSData
import pandas as pd
import os

def run_for_single_stock_by_date(code, dt):
    with GetCCASSData() as gcas:
        gcas.click_date(dt)
        gcas.enter_stock(code)
        try:
            gcas.click_date(dt)
            gcas.click_search_button()
            df = gcas.read_main_table()
            curdt = gcas.get_current_date()
            df.assign(code=str(code), date=curdt)
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
