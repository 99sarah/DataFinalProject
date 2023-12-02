import numpy as np

from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning
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
            dcc.Dropdown(
                kResponseTrackerDf.CountryName.unique(),
                id='country-selection',
                value=['Germany'],
                multi=True,
                className='dbc'
            ),
            dcc.Dropdown(
                kCovidDf.columns,
                id='covid-trend-selection',
                value='new_cases_smoothed_per_million',
                className='dbc'
            ),
            dcc.Graph(id='covid-trend-chart'),
            dcc.Dropdown(
                kResponseOrdinalMeaning[['Name', 'Description']].rename(
                    columns={'Name': 'value', 'Description': 'label'}).to_dict('records'),
                id='metric-selection',
                value='C1M_School closing',
                className='dbc'
            ),
            dcc.Graph(id='response-chart'),
            html.Div(id='my-output-d')
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
    print(f'{country_names}, {covid_trend_metric}, {metric_name}')
    startDate = np.datetime64('2020-03-01')
    endDate = np.datetime64('2022-09-01')
    covid_trend_chart = px.line(
        kCovidDf.query("location in @country_names and @startDate < date < @endDate"),
        color='location',
        x='date',
        y=covid_trend_metric
    ).update_xaxes(
        showspikes=True,
        spikecolor="white",
        spikesnap="cursor",
        spikemode="across",
        spikedash="solid",
    )  # .update_traces(xaxis="x4")
    response_chart = px.line(
        kResponseTrackerDf.query("CountryName in @country_names and @startDate < Date < @endDate"),
        color='CountryName',
        x='Date',
        y=metric_name
    ).update_xaxes(
        showspikes=True,
        spikecolor="white",
        spikesnap="cursor",
        spikemode="across",
        spikedash="solid",
    )  # .update_traces(xaxis="x4")

    return covid_trend_chart, response_chart


@callback(
    Output('my-output-d', 'children'),
    Input('covid-trend-chart', 'hoverData'),
)
def cross_filtering(hover_data):
    if not hover_data:
        raise PreventUpdate
    date = hover_data['points'][0]['x']
    return f'Output: {date}'
# TODO Spikeline across both graphs
