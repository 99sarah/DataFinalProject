import numpy as np
import plotly.graph_objects

from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data.covidData import kCovidDf
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

k_line_color_palett = ['rgb(50,76,113)', 'rgb(183,30,29)', 'rgb(0,189,139)', 'rgb(236,157,14)', 'rgb(110,175,245)']

responseTrackerTab = dcc.Tab(
    label='Response Tracker',
    children=[
        html.Div(children=[
            dcc.Dropdown(
                kResponseTrackerDf.CountryName.unique(),
                id='location_selection',
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
            dcc.Dropdown(
                kResponseOrdinalMeaning[['Name', 'Description']].rename(
                    columns={'Name': 'value', 'Description': 'label'}).to_dict('records'),
                id='metric-selection',
                value='C1M_School closing',
                className='dbc'
            ),
            html.Div(id='my-output-d'),
            dcc.Graph(id="sub-plots")
        ])
    ])


# @callback(
#     Output('my-output-d', 'children'),
#     Input('corona_trend_graph', 'hoverData'),
# )
# def cross_filtering(hover_data):
#     if not hover_data:
#         raise PreventUpdate
#     date = hover_data['points'][0]['x']
#     return f'Output: {date}'


@callback(
    Output('corona_trend_graph', 'figure'),

    [Input('location_selection', 'value'),
     Input('covid-trend-selection', 'value'),
     Input('metric-selection', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')]
)
def update_graph(country_names, covid_trend_metric, response_metric_name, start_date, end_date):
    nested_plot = make_subplots(rows=2, cols=1, shared_xaxes=True)

    covid_pre_filter = kCovidDf.query("location in @country_names and @start_date < date < @end_date")
    response_pre_filter = kResponseTrackerDf.query("CountryName in @country_names and @start_date < Date < @end_date")
    i = 0
    for country in country_names:
        covid_country = (covid_pre_filter.query('location == @country')),
        covid_graph = go.Scatter(
            x=covid_country[0]['date'],
            y=covid_country[0][covid_trend_metric],
            legendgroup=country,
            name=country,
            mode='lines',
            marker=dict(color=k_line_color_palett[i % (len(k_line_color_palett))])
        )
        nested_plot.add_trace(covid_graph, row=1, col=1)

        response_country = response_pre_filter.query('CountryName == @country')
        response_graph = go.Scatter(
            x=response_country['Date'],
            y=response_country[response_metric_name],
            legendgroup=country,
            name=country,
            marker=dict(color=k_line_color_palett[i % (len(k_line_color_palett))]),
            showlegend=False,
        )
        response_graph.update(dy=1)
        nested_plot.add_trace(response_graph, row=2, col=1)
        i += 1
    # configure hover information
    nested_plot.update_xaxes(showspikes=True, spikemode="across")
    nested_plot.update_traces(xaxis="x2")
    nested_plot.update_layout(hovermode="x")
    return nested_plot
