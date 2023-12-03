from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import json
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from matplotlib.dates import date2num, num2date
from data.covidData import kCovidDf

cov_df_grouped = kCovidDf.groupby(['iso_code', 'date']).sum().reset_index()
cov_df_grouped = cov_df_grouped[~(cov_df_grouped.iso_code.str.startswith('OWID', na=False))]

# date_converter = pd.DataFrame()
# date_converter['value'] = kCovidDf['date']
# date_converter['key'] = date_converter['value'].astype(np.int64)
# date_converter.set_index('date_as_int')

top_filter = dbc.Card(id='top_filter',
                      # children=[
                      #     dcc.Slider(
                      #         id='date_slider',
                      #         min=date_converter['key'].min(),
                      #         max=date_converter['key'].max(),
                      #         value=date_converter['key'].min(),
                      #         # marks=date_converter.to_dict('records'),
                      #         step=None
                      #     )
                      # ]
                      )
left_filter = dbc.Card(id='left_filter',
                       children=[
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
                               className='dbc'
                           ),

                           dbc.Col(children=[
                               dcc.DatePickerRange(
                                   id='date_range_picker',
                                   start_date=kCovidDf['date'].min(),
                                   end_date=kCovidDf['date'].max(),
                                   className='dbc'
                               )]),
                           dbc.Col(children=[
                               dcc.Dropdown(
                                   kCovidDf.location.unique(),
                                   id='location_selection',
                                   value=['Germany'],
                                   multi=True,
                                   className='dbc'
                               )]),
                       ])
corona_map = dbc.Card(id='corona_map',
                      children=[dcc.Loading(dcc.Graph(id='corona_map_graph'))]
                      )
corona_bubble = dbc.Card(id='corona_bubble',
                         children=[dcc.Loading(dcc.Graph(id='corona_bubble_graph'))]
                         )
corona_trend = dbc.Card(id='corona_trend',
                        children=[dcc.Loading(dcc.Graph(id='corona_trend_graph'))]
                        )
response_trend = dbc.Card(id='response_trend',
                          children=[dcc.Loading(dcc.Graph(id='corona_response_graph'))]

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
                    children=[left_filter],
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[top_filter]

                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[corona_map],
                                ),
                                dbc.Col(
                                    children=[corona_trend],
                                )
                            ],
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[corona_bubble],
                                ),
                                dbc.Col(
                                    children=[response_trend],
                                )
                            ]
                        )
                    ],
                    width=10
                )]
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
    cov_df_in_range = cov_df_grouped[cov_df_grouped['date'].between(start_date, end_date)]
    cov_df = cov_df_in_range[['iso_code', 'location', 'new_cases']]
    cov_df = cov_df.groupby(['iso_code', 'location']).sum().reset_index()
    # show map
    format = '%m/%d/%Y'
    fig = px.choropleth(cov_df,
                        locations='iso_code',
                        color='new_cases',
                        locationmode='ISO-3',
                        scope=continent,
                        hover_name='location',
                        # animation_frame=cov_df['date'].dt.date,
                        range_color=(cov_df['new_cases'].min(),
                                     cov_df['new_cases'].max()),
                        color_continuous_scale=px.colors.sequential.solar,
                        title=f'New Cases between {pd.to_datetime(start_date).strftime(format)} and {pd.to_datetime(end_date).strftime(format)}'
                        )
    return [fig]


# @callback(
#     Output('location_selection', 'value'),
#     Input('corona_map_graph', 'selectedData'))
# def display_selected_data(selected_data):
#     selected_points_all = cov_df_grouped['location']
#     if selected_data and selected_data["points"]:
#         selected_points = np.intersect1d(
#             selected_points_all, [p["hovertext"] for p in selected_data["points"]]
#         )
#         print(selected_points.dtype)
#         return selected_points
#     return ['Germany']

@callback(
    Output('location_selection', 'value'),
    Output('corona_map_graph', 'clickData'),
    Input('corona_map_graph', 'clickData'),
    Input('location_selection', 'value'))
def display_click_data(click_data, options):
    selected_points_all = cov_df_grouped['location']
    if click_data:
        selected_points = np.intersect1d(
            selected_points_all, [p["hovertext"] for p in click_data["points"]]
        )
        selected_points = np.union1d(
            selected_points, options
        )
        return [selected_points, None]
    return [options, None]

# @callback(
#     Output('top_filter','children'),
#     [Input('date_range_picker', 'start_date'),
#      Input('date_range_picker', 'end_date'),]
# )
# def update_slider(start_date, end_date):
#     if not start_date or not end_date:
#         raise PreventUpdate
#     return [dcc.Slider(
#                           id='date_slider',
#                           min=0,
#                           max=500,
#                           value=0,
#                           #marks={date_converter['date_as_int']: date_converter['date'] for date_as_int, year in date_converter['date'].to_dict()},
#                           #step=1
#                       )]
