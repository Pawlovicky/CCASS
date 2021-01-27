from .GetCCASSData import GetCCASSData
import pandas as pd
import os

class CCASSDownloadManager:
    
    def __init__(self):
        self.taskdf = None
        
    def get_full_task_list(self):
        """
        One task is defined as a stock at a specific date. Valid stocks are
        defined for a specific date, with 1 year of history available.
        Get the valid stock list for all business days over the last 1 year
        """
        with GetCCASSData() as gcas:
            curdt = gcas.defaultdate
            sdt = curdt - pd.to_timedelta('365 days')
            rng = pd.bdate_range(sdt, curdt)
            dfs = []
            for dt in rng:
                df = gcas.get_list_of_stocks_asof(dt).stocks.assign(date=dt)
                dfs.append(df)
        self.taskdf = pd.concat(dfs)
        return self
    
    def _fix_formatting(self):
        kcols = ['Stock Code', 'Stock Name', 'date']
        df = self.taskdf.loc[:, kcols].reset_index(drop=True)
        df.columns = ['code', 'name', 'date']
        ashares = df['name'].str.contains('A #')
        df.loc[~ashares, 'bbcode'] = df.loc[~ashares, 'code'].astype(str) + ' HK'
        df.loc[ashares, 'bbcode']  = df.loc[ashares, 'name'].str.split('#')\
                                        .str.get(1).str.slice(0, 6) + ' CH'
        self.taskdf = df
        return self
        
        
    def filter_tasks(self):
        """
        Filter the securities by securities from HSCI/CSI 300/CSI 500
        """
        def load_eligible_tickers():
            def fp(lstr):
                lfn = ['CCASS_SCRAPER', 'files', lstr]
                return os.path.join(*lfn)
            c3 = pd.read_csv(fp('csi300.csv'))['成分券代码Constituent Code'].astype(str).str.zfill(6) + ' CH'
            c5 = pd.read_csv(fp('csi500.csv'))['成分券代码Constituent Code'].astype(str).str.zfill(6) + ' CH'
            hs = pd.read_csv(fp('hsci.csv'))['Code'].astype(str) + ' HK'
            keepcodes = pd.concat([c3, c5, hs]).to_frame('bbcode')
            return keepcodes
        self._fix_formatting()
        keepcodes = load_eligible_tickers().assign(inuniverse = True)
        self.taskdf = self.taskdf.merge(keepcodes, on='bbcode', how='left')
        self.taskdf = self.taskdf.loc[self.taskdf['inuniverse'].fillna(False)]
        return self
    
    def slice_tasks_for_multiprocessing(self):
        """
        Pass tuples of stocks and dates 
        """
        pass
    
    def save(self):
        self.taskdf.to_csv(os.path.join('files', 'all_tasks.csv.zip'), index=False)
    
    def load(self, fn='scheduled_tasks'):
        #self.taskdf= pd.read_csv(os.path.join('files', 'all_tasks.csv.zip'))
        lfn = ['CCASS_SCRAPER', 'files', 'all_tasks.csv.zip']
        self.taskdf= pd.read_csv(os.path.join(*lfn))
        return self
