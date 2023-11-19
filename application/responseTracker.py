from data.covidData import kCovidDf, kResponseTrackerDf
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data.covidData import kCovidDf
from dash.exceptions import PreventUpdate

responseTrackerTab = dcc.Tab(
    label='Response Tracker',
    children=[
        html.Div(children=[
            dcc.Dropdown(kResponseTrackerDf.CountryName.unique(), id='country-selection', value='Germany', multi=True),
            dcc.Dropdown(kCovidDf.columns, id='covid-trend-selection', value='C1M_School closing'),
            dcc.Graph(id='covid-trend-chart'),
            dcc.Dropdown(kResponseTrackerDf.columns, id='metric-selection', value='C1M_School closing'),
            dcc.Graph(id='response-chart')
        ])
    ])


@callback(
    [Output('covid-trend-chart', 'figure'),
     Output('response-chart', 'figure')],
    [Input('country-selection', 'value'),
    Input('covid-trend-selection', 'value'),
     Input('metric-selection', 'value')]
)
def update_graph(country_names, covid_trend_metric, metric_name):
    covid_trend_chart = px.line(
        kCovidDf[kCovidDf['iso_code'] == 'DEU'][covid_trend_metric],
        color='CountryName',
        x='Date',
        y=metric_name
    )
    response_chart = px.line(
        kResponseTrackerDf.query("CountryName in @country_names"),
        color='CountryName',
        x='Date',
        y=metric_name
    )

    return covid_trend_chart, response_chart
