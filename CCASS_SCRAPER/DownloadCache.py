import pandas as pd
from CCASS_SCRAPER import run_ccass as rc

class DownloadCache:
    def __init__(self):
        self.fn = 'datacache.csv'
        self.df = None
    
    def load(self):
        self.df = pd.read_csv(self.fn, parse_dates=['date'])
        self.df.loc[:, 'code'] = self.df['code'].astype(int)
        return self
    
    def save(self):
        self.df = self.df.drop_duplicates()
        self.df.to_csv(self.fn, index=False)
        return self
    
    def _append(self, df):
        df.to_csv(self.fn, header=False, mode='a', index=False)
        return self
    
    def download_single_stock(self, sdt, edt, code):
        dts = pd.bdate_range(sdt, edt)
        dts = dts.union(pd.DatetimeIndex([edt]))
        assert len(dts) > 0
        if self.df is not None:
            xdates = self.df.loc[self.df['code']==code, 'date'].unique()
            dts = dts[~dts.isin(xdates)]
            if len(dts) == 0:
                return self
            df = rc.download_single_stock_by_daterange(dts, code)
            if df is None:
                return self
            df.loc[:, 'code'] = df['code'].astype(int)
            xdates = self.df.loc[self.df['code']==code, 'date'].unique()
            df = df.loc[~df['date'].isin(xdates)]
            self._append(df)
            self.df = pd.concat([self.df, df]).sort_values(['date', 'code'])
            self.df = self.df.reset_index(drop=True)
        else:
            df = rc.download_single_stock_by_daterange(dts, code)
            df.loc[:, 'code'] = df['code'].astype(int)
            self.df = df.reset_index(drop=True)
            self.save()
        return self
    
    def add_features_for_diff_shares_and_output(self):
        def add_diff_shareholding(df):
            colnm = 'shareholding'
            df = df.sort_values(['date', 'code'])
            df.loc[:, 'diff_'+colnm] = df.groupby(['code', 'pid'])[colnm].diff()
            return df
        
        def add_pct_shareholding(df):
            df = df.merge(df.groupby(['date', 'code'])['shareholding']\
                   .sum().to_frame('tot_shares'), on=['date', 'code'], how='left')
            df.loc[:, 'pctdiffshares'] = df['diff_shareholding']/df['tot_shares']
            return df
        
        df = add_diff_shareholding(self.df)
        df = add_pct_shareholding(df)
        df.loc[:, 'date'] = pd.to_datetime(df['date'].dt.date, errors='coerce')
        df.loc[:, 'code'] = df['code'].astype(int)
        return df
