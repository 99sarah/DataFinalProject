import numpy as np
import plotly.graph_objects

from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data.covidData import kCovidDf, get_label
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

k_line_color_palett = ['rgb(50,76,113)', 'rgb(183,30,29)', 'rgb(0,189,139)', 'rgb(236,157,14)', 'rgb(110,175,245)']

@callback(
    Output('response_legend', 'children'),

    [Input('corona_trend_graph', 'hoverData'),
     Input('metric-selection', 'value'), ]
)
def legend_ordinal_response(hover_data, response_metric):
    if not hover_data:
        hover_data = dict({'points': []})
    response_metric_description = kResponseOrdinalMeaning.query('Name == @response_metric')['Description'][0]
    ordinal_values = list(map(lambda point: point['y'], hover_data['points']))
    ordinal_coding = kResponseOrdinalMeaning.query('Name == @response_metric')['Coding'].to_dict()[0].split('+')
    ordered_list = []
    i = 0
    for ordinal_code in ordinal_coding:
        if i in ordinal_values:
            ordered_list.append(html.Li(html.Span(ordinal_code, style={'color': 'white'}), style={'color': 'red'}))
        else:
            ordered_list.append(html.Li(ordinal_code))
        i += 1
    return html.Div(
        children=[
            html.H6(
                f'Index decoding of "{response_metric_description}":'
            ),
            html.Ul(
                ordered_list
            )
        ]
    )


@callback(
    Output('corona_trend_graph', 'figure'),

    [Input('location_selection', 'value'),
     Input('covid-trend-selection', 'value'),
     Input('metric-selection', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')]
)
def update_graph(country_names, covid_trend_metric, response_metric_name, start_date, end_date):
    response_metric_description = kResponseOrdinalMeaning.query('Name == @response_metric_name')['Description'][0]
    nested_plot = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.9, 0.3], vertical_spacing=0.1,
                                subplot_titles=(get_label(covid_trend_metric), response_metric_description))

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
    nested_plot.update_layout(hovermode="x", height=600, title='Trend view')

    nested_plot.update_yaxes(title_text="Quantity", row=1, col=1)

    nested_plot.update_xaxes(title_text="Time", row=2, col=1)
    nested_plot.update_yaxes(title_text="Index", row=2, col=1)
    return nested_plot
