from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import json
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from matplotlib.dates import date2num, num2date
from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning, kCovid_Response, date_format
import application.responseTracker

SIDEBAR_STYLE = {
    "margin-bottom": "2rem",
}

STYLE = {
    "margin-top": "1rem",
    "margin-left": "1rem",
    "margin-right": "1rem",
    "margin-bottom": "1rem",
}

left_filter = dbc.Card(html.Div(id='left_filter',
                                style=STYLE,
                                children=[
                                    html.H6('Choose a continent:'),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'World', 'value': 'world'},
                                            {'label': 'Europe', 'value': 'europe'},
                                            {'label': 'North America', 'value': 'north america'},
                                            {'label': 'South America', 'value': 'south america'},
                                            {'label': 'Asia', 'value': 'asia'},
                                            {'label': 'Africa', 'value': 'africa'},
                                        ],
                                        id='continent_dropdown',
                                        value='world',
                                        className='dbc',
                                        style=SIDEBAR_STYLE
                                    ),

                                    dbc.Col(children=[
                                        html.H6('Choose a time period:'),
                                        dcc.DatePickerRange(
                                            id='date_range_picker',
                                            start_date=kCovidDf['date'].min(),
                                            end_date=kCovidDf['date'].max(),
                                            className='dbc',
                                            style=SIDEBAR_STYLE
                                        )]),
                                    dbc.Col(
                                        children=[
                                            html.H6('Pick countries:'),
                                            dcc.Dropdown(
                                                kResponseTrackerDf.CountryName.unique(),
                                                id='location_selection',
                                                value=['Germany'],
                                                multi=True,
                                                className='dbc',
                                                style=SIDEBAR_STYLE
                                            )]),

                                ]))
top_filter = dbc.Card(id='top_filter')
corona_map = dbc.Card(id='corona_map',
                      children=[dcc.Loading(dcc.Graph(id='corona_map_graph'))]
                      )
corona_bubble = dbc.Card(id='corona_bubble',
                         children=[dcc.Graph(id='corona_bubble_graph')]
                         )
response_legend = html.Div(id='response_legend', )
response_dropdown = dbc.Row(
    children=[dbc.Col(
        children=[
            html.H6('Choose a covid metric:'),
            dcc.Dropdown(
                kCovidDf.columns,
                id='covid-trend-selection',
                value='new_cases_smoothed_per_million',
                className='dbc',
            ),
        ],
        style=STYLE

    ),

        dbc.Col(
            children=[
                html.H6('Choose a national response metric:'),
                dcc.Dropdown(
                    kResponseOrdinalMeaning[['Name', 'Description']].rename(
                        columns={'Name': 'value', 'Description': 'label'}).to_dict('records'),
                    id='metric-selection',
                    value='C1M_School closing',
                    className='dbc',
                ),
            ],
            style=STYLE

        ), ]
)
corona_trend = dbc.Card(id='corona_trend',
                        children=[
                            response_dropdown,
                            dcc.Loading(dcc.Graph(id='corona_trend_graph')),
                            response_legend
                        ]
                        )
stringency_bar = dbc.Card(
    id='stringency_bar',
    children=[dcc.Graph(id='stringency_bar_chart')]
)

analysisTab = dcc.Tab(
    label='Analysis',
    value='analysisTab',
    children=[
        html.H1(
            children='Analysis of covid-19',
            style={'textAlign': 'center'}
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[top_filter]

                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        dbc.Row(
                                            children=[
                                                dbc.Col(
                                                    children=[left_filter],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    children=[corona_map],
                                                ),
                                            ],
                                        ),
                                        dbc.Row(
                                            children=[
                                                dbc.Col(
                                                    children=[stringency_bar],
                                                    width=5
                                                ),
                                                dbc.Col(
                                                    children=[corona_bubble],
                                                )
                                            ],
                                        ),
                                    ],
                                    width=6
                                ),
                                dbc.Col(
                                    children=[corona_trend],
                                    width=6
                                )
                            ],
                        ),
                    ],
                ),

            ]
        )
    ]
)


@callback(
    [Output('corona_map_graph', 'figure')],
    [Input('continent_dropdown', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date')]
)
def update_graphs(continent, start_date, end_date):
    if not continent or not start_date or not end_date:
        raise PreventUpdate
    # filter data between given dates
    cov_df_in_range = kCovidDf[kCovidDf['date'].between(start_date, end_date)]
    cov_df = cov_df_in_range[['iso_code', 'location', 'new_cases']]
    cov_df = cov_df.groupby(['iso_code', 'location']).sum().reset_index()
    # show map
    fig = px.choropleth(cov_df,
                        locations='iso_code',
                        color='new_cases',
                        locationmode='ISO-3',
                        scope=continent,
                        hover_name='location',
                        range_color=(cov_df['new_cases'].min(),
                                     cov_df['new_cases'].max()),
                        color_continuous_scale=px.colors.sequential.solar,
                        title=f'New Cases between {pd.to_datetime(start_date).strftime(date_format)} and {pd.to_datetime(end_date).strftime(date_format)}'
                        )
    fig.update_layout(margin=dict(t=45, r=2, l=5, b=20))
    fig.update_layout(coloraxis=dict(colorbar=dict(orientation='h', y=-0.15)))
    return [fig]


@callback(
    Output('location_selection', 'value'),
    Output('corona_map_graph', 'clickData'),
    Input('corona_map_graph', 'clickData'),
    Input('location_selection', 'value'))
# clicked country from map is added to selected options in dropdown
def display_click_data(click_data, options):
    selected_points_all = kCovidDf['location']
    if click_data:
        selected_points = np.intersect1d(
            selected_points_all, [p["hovertext"] for p in click_data["points"]]
        )
        selected_points = np.union1d(
            selected_points, options
        )
        return [selected_points, None]
    return [options, None]


def create_bubble_chart(dff, metric, max_x, max_y, title):
    fig = px.scatter(
        dff,
        x='new_cases_smoothed',
        y='new_deaths_smoothed',
        color='location',
        size_max=20,
        range_x=[0, max_x],
        range_y=[0, max_y],
        title=title,
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(rangemode="tozero")
    fig.update_traces(marker={'size': 20})

    return fig


@callback(
    Output('corona_bubble_graph', 'figure'),
    [Input('location_selection', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date'),
     Input('metric-selection', 'value'),
     Input('corona_trend_graph', 'hoverData'),
     ]
)
def update_bubble_chart(countries, start_date, end_date, metric, date_hover):
    if not countries:
        raise PreventUpdate
    if date_hover:
        date = date_hover['points'][0]['x']
    else:
        date = start_date
    filtered_df = kCovid_Response[(kCovid_Response['location'].isin(countries))]
    max_x = filtered_df.where(filtered_df['date'].between(start_date, end_date))['new_cases_smoothed'].max()
    max_y = filtered_df.where(filtered_df['date'].between(start_date, end_date))['new_deaths_smoothed'].max()
    filtered_df = filtered_df[(filtered_df['date'] == date)]
    title = f'Comparison of new cases and new deaths on {pd.to_datetime(date).strftime(date_format)}'
    return create_bubble_chart(filtered_df, metric, max_x, max_y, title)


@callback(
    Output('stringency_bar_chart', 'figure'),
    [Input('location_selection', 'value'),
     Input('date_range_picker', 'start_date'),

     Input('corona_trend_graph', 'hoverData'), ]
)
def update_bar_chart(countries, start_date, hover_data):
    if not countries:
        raise PreventUpdate
    if not hover_data:
        date = start_date
    else:
        date = hover_data['points'][0]['x']
    filtered_df = kCovid_Response[(kCovid_Response['location'].isin(countries))]
    filtered_df = filtered_df[(filtered_df['date'] == date)]
    fig = px.bar(
        filtered_df,
        x='location',
        y='stringency_index',
        range_y=[0, 100],
        title=f'Stringency index on {pd.to_datetime(date).strftime(date_format)}',
        color='location'
    )
    return fig
