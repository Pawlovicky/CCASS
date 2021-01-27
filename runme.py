from CCASS_SCRAPER.CCASSDownloadManager import CCASSDownloadManager
from CCASS_SCRAPER import run_ccass as rc
from selenium import webdriver
from multiprocessing import Pool
import pandas as pd
import os


def download_and_save():
    cdl = CCASSDownloadManager().load().filter_tasks()
    selcodes = [175, 241, 267, 270, 291, 384, 386, 586, 688, 700, 762, 2382, 2601]
    sdf = cdl.taskdf.loc[cdl.taskdf['code'].isin(selcodes)]
    rlist = sdf.set_index('date')\
               .loc[:, ['code']].to_records().tolist()
    n = 10
    lofl = [rlist[i::n] for i in range(n)]
    p = Pool(10)
    dfs = p.map(rc.run_for_all_stocks_by_records, lofl)
    tdf = pd.concat(dfs)
    tdf.to_csv('partip.csv.zip', index=False)

if __name__ == "__main__":
    download_and_save()