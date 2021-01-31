import pandas as pd
import numpy as np

def generate_df(sdt, edt, n=30):
    dts = pd.bdate_range(sdt, edt)
    assert len(dts) > 0
    shp1 = [dts.shape[0], n]
    chngs = np.random.randn(*shp1)*0.01
    df = (pd.DataFrame(chngs)+1).cumprod()
    cumsum = pd.Series(np.random.uniform(0, 1, n+1)).sort_values().diff().dropna()
    df = df*cumsum.values
    df.index = dts
    df = df.stack()
    df = df.rename_axis(['date', 'owner']).to_frame('ownership').reset_index()
    return df

def select_top_10(df):
    dt = df['date'].max()
    first10 = df.loc[df['date'] == dt].sort_values('ownership', ascending=False).head(10)['owner']
    df = df.loc[df['owner'].isin(first10)]
    return df

def get_holdings_test_data(sdt, edt, code):
    df = generate_df(sdt, edt, n=30)
    df = select_top_10(df)
    df = df.assign(code=code)
    return df