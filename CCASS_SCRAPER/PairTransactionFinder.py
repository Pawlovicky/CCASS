import pandas as pd
import numpy as np
from CCASS_SCRAPER.DownloadCache import DownloadCache


def load_and_make_transaction_screen(sdt, edt, code, thresh):
    try:
        dcache = DownloadCache().load()
    except FileNotFoundError:
        dcache = DownloadCache()
    dcache = dcache.download_single_stock(sdt, edt, code)
    df = dcache.add_features_for_diff_shares_and_output()
    ptf = PairTransactionFinder(df, code)
    ptf = ptf.create_all_pairs()
    ptf = ptf.add_shareholder_changes_table(thresh=thresh)
    ptf = ptf.add_discovery_features()
    screen = ptf.output_screening(thresh=thresh)
    return screen

class PairTransactionFinder:
    def __init__(self, df, code):
        self.df = df.loc[df['code'] == code]
    
    def create_all_pairs(self):
        pids = self.df['pid'].unique()
        ididxes = list(range(len(pids)))
        print(len(pids))
        pidx = pd.MultiIndex.from_product([ididxes, ididxes])
        pidx = pd.DataFrame(index=pidx).reset_index()
        pidx.columns = ['pid_i','pid_j']
        pidx = pidx.loc[pidx['pid_i'] < pidx['pid_j']]
        pidx = pd.concat([pd.DataFrame(pids).reindex(pidx['pid_i'])\
                            .reset_index(drop=True), 
                          pd.DataFrame(pids).reindex(pidx['pid_j'])\
                             .reset_index(drop=True)],
                  axis=1)
        pidx.columns = ['pid_i', 'pid_j']
        kcols = ['date', 'code']
        pidx = pidx.assign(key=0).merge(self.df.loc[:, kcols].drop_duplicates()\
                                     .assign(key=0),
                                 how='outer', on='key').drop('key', axis=1)\
                          .sort_values(['date'])
        self.pdf = pidx
        return self
    
    def add_shareholder_changes_table(self, thresh=0.001):
        kcols = ['date', 'pid', 'pname', 'diff_shareholding', 'pctdiffshares']
        ren2i= dict(zip(kcols[1:], [x+'_i' for x in kcols[1:]]))
        ren2j = dict(zip(kcols[1:], [x+'_j' for x in kcols[1:]]))
        rencols = {'pid':'pid_i'}
        self.pdf = self.pdf.merge(self.df.loc[:, kcols].rename(columns=ren2i),
                       on=['date', 'pid_i'], how='left')\
                       .dropna(subset=['pctdiffshares_i'])
        thresh = self.pdf['pctdiffshares_i'].abs() > thresh
        self.pdf = self.pdf.loc[thresh]
        self.pdf = self.pdf.merge(self.df.loc[:, kcols].rename(columns=ren2j),
                       on=['date', 'pid_j'], how='left')
        return self
    
    def add_discovery_features(self):       
        # estimate the noise from the non-zero transactions only
        self.pdf.loc[:, '|dsi + dsj|'] = (self.pdf['diff_shareholding_i']+\
                                          self.pdf['diff_shareholding_j']).abs()
        absdsi_dsj = self.pdf['diff_shareholding_i'].abs()\
                    +self.pdf['diff_shareholding_j'].abs()
        colnm =  '|dsi + dsj|/(|dsi| + |dsj|)'
        self.pdf.loc[:, colnm] = self.pdf['|dsi + dsj|']/absdsi_dsj
        self.pdf.loc[:, '(si-sj)^2'] = (self.pdf['pctdiffshares_i'] -\
                                       self.pdf['pctdiffshares_j'])**2
        self.pdf.loc[self.pdf['(si-sj)^2'] == 0, '(si-sj)^2'] = np.nan
        nrm = self.pdf.groupby(['date', 'code'])['(si-sj)^2']\
                  .apply(lambda x:np.sqrt(np.mean(x)))\
                  .to_frame('sqrt(sum(si-sj)^2)')\
                  .reset_index()
        self.pdf = self.pdf.merge(nrm, on=['date', 'code'], how='left')
        self.pdf.loc[:, '|si + sj|'] = (self.pdf['pctdiffshares_i'] +\
                                       self.pdf['pctdiffshares_j']).abs()
        self.pdf.loc[:, 'n|si + sj|'] = self.pdf['|si + sj|']/\
                                       self.pdf['sqrt(sum(si-sj)^2)']
        
        return self
    
    def output_screening(self, thresh=0.001):
        colnm = '|dsi + dsj|/(|dsi| + |dsj|)'
        threshrule = self.pdf['pctdiffshares_i'].abs() > thresh
        threshrule = threshrule & (self.pdf[colnm] < 0.1)
        colnm = '|dsi + dsj|/(|dsi| + |dsj|)'
        screen = self.pdf.loc[threshrule].sort_values(['date', colnm])
        kcols = ['date', 'pid_i', 'pid_j', 'pname_i', 'pname_j', 
                 'diff_shareholding_i', 'diff_shareholding_j',
                 '|dsi + dsj|/(|dsi| + |dsj|)', 'pctdiffshares_i', 'pctdiffshares_j']
        screen = screen.loc[:, kcols]
        kcols = ['date', 'pid_i', 'pid_j', 'pname_i', 'pname_j', 
                 'diff_shareholding_i', 'diff_shareholding_j',
                 '|dsi + dsj|/(|dsi| + |dsj|)', 'ndsi_i', 'ndsi_j']
        screen.columns = kcols
        rcols = ['|dsi + dsj|/(|dsi| + |dsj|)', 'ndsi_i', 'ndsi_j']
        for col in rcols:
          screen.loc[:, col] = screen[col].round(5)
        return screen
    
        
        
