#!/usr/bin/python3
import argparse
from CCASS_SCRAPER.TestData import get_holdings_test_data
from CCASS_SCRAPER import run_ccass as rc
import pandas as pd
from datetime import date
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import DataTable
from CCASS_SCRAPER import PairTransactionFinder as PTF


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


edt = rc.get_current_date()
sdt = edt - pd.to_timedelta('365 days')
desc = """LEGEND

diff_shareholding_i,j: difference between current and previous date shareholding

dsi/dsj: diff_shareholding_i,j

ndsi/ndsj: difference in shareholdings normalized with total shareholdings

=====================================

Screening is conducted by filtering
- ndsi < threshold
- |dsi + dsj|/(|dsi| + |dsj|) < 0.1

Note that the screen will filter this for any day given, to get a history
of potential pair transactions.
       """


def datepicker(sdt, edt, idnm='my-date-picker-single'):
    fn = dcc.DatePickerSingle(
        id=idnm,
        min_date_allowed=sdt,
        max_date_allowed=edt,
        initial_visible_month=edt,
        date=edt
    )
    return fn

app.layout = html.Div([
    html.H2('CCASS Participation Transaction Screening'),
    datepicker(sdt, edt, 'start-date'),
    datepicker(sdt, edt, 'end-date'),
    dcc.Input(id='code', value=1, type='number'),
    dcc.Input(id='threshold', value=0.01, type='number'),
    html.Button('Update', id='download-button-state', n_clicks=0),
    DataTable(id='table', data=[], filter_action='native'),
    dcc.Markdown(desc)
])


@app.callback(
    [Output('table', 'data'),
     Output('table', 'columns')],
    Input('download-button-state', 'n_clicks'),
    State('start-date', 'date'),
    State('end-date',   'date'),
    State('code',   'value'),
    State('threshold',   'value'))

def update_output(nclicks, sdate, edate, code, threshold):
    ldf = PTF.load_and_make_transaction_screen(sdate, edate, code, threshold)
    columns = [{'name':i, 'id':i} for i in ldf.columns]
    data = ldf.to_dict('records')
    return data, columns

if __name__ == '__main__':
    # fix this as it should run on a wsgi server
    app.run_server(debug=True, host='0.0.0.0', port=8051)
