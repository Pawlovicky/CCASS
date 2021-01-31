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

desc = "This starts the dashboard for the Top 10 Shareholders. If --testdata is passed, it will not scrape but use functions provided in testdata. This can be used to test the engine if the scrapped side is under maintenance (e.g. Sundays)."
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('--testdata', action='store_true',
                    help='A boolean switch')
args = parser.parse_args()

if args.testdata:
    fn = get_holdings_test_data
    print('use testdata')
else:
    fn = rc.download_single_stock

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

edt = rc.get_current_date()
sdt = edt - pd.to_timedelta('365 days')

def datepicker(mdate, edate, idnm='my-date-picker-single'):
    fn = dcc.DatePickerSingle(
        id=idnm,
        min_date_allowed=sdt,
        max_date_allowed=edt,
        initial_visible_month=edt,
        date=edt
    )
    return fn

app.layout = html.Div([
    html.Title('CCASS Ownership Trend Plot'),
    datepicker(sdt, edt, 'start-date'),
    datepicker(sdt, edt, 'end-date'),
    dcc.Input(id='code', value=0, type='number'),
    html.Button('Download', id='download-button-state', n_clicks=0),
    DataTable(id='table', data=[], filter_action='native'),
    dcc.Graph(id='time-series-chart')
])


@app.callback(
    [Output('table', 'data'),
     Output('table', 'columns'),
     Output('time-series-chart', 'figure')],
    Input('download-button-state', 'n_clicks'),
    State('start-date', 'date'),
    State('end-date',   'date'),
    State('code',   'value'))

def update_output(nclicks, sdate, edate, code):
    df = fn(sdate, edate, code)
    fig = px.line(df, x='date', y='ownership', color='owner')
    ldf = df.loc[df['date'] == edate].sort_values('ownership', ascending=False)
    columns = [{'name':i, 'id':i} for i in ldf.columns]
    data = ldf.to_dict('records')
    return data, columns, fig

if __name__ == '__main__':
    # fix this as it should run on a wsgi server
    app.run_server(debug=True, host='0.0.0.0')
