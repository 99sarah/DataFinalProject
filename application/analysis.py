from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import json
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from matplotlib.dates import date2num, num2date
from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning
import application.responseTracker

cov_df_grouped = kCovidDf.groupby(['iso_code', 'date']).sum().reset_index()
cov_df_grouped = cov_df_grouped[~(cov_df_grouped.iso_code.str.startswith('OWID', na=False))]
values_per_country = kCovidDf[
    ['iso_code', 'location', 'stringency_index', 'people_vaccinated', 'aged_65_older', 'population']].groupby(
    ['iso_code', 'location']).mean().dropna().reset_index()
merge_1_df = pd.DataFrame()
merge_1_df[['iso_code', 'location', 'date', 'stringency_index']] = kResponseTrackerDf[['CountryCode', 'CountryName', 'Date', 'StringencyIndex_Average']]
merge_1_df.set_index(['iso_code', 'location', 'date'], inplace=True)
merge_2_df = pd.DataFrame()
merge_2_df[['iso_code', 'location', 'date', 'new_cases_smoothed', 'new_deaths_smoothed']] = kCovidDf[['iso_code', 'location', 'date', 'new_cases_smoothed', 'new_deaths_smoothed']]
merge_2_df.set_index(['iso_code', 'location', 'date'], inplace=True)
merged_df = pd.concat([merge_1_df, merge_2_df], axis=1, join='inner')
merged_df.reset_index(inplace=True)


# date_converter = pd.DataFrame()
# date_converter['value'] = kCovidDf['date']
# date_converter['key'] = date_converter['value'].astype(np.int64)
# date_converter.set_index('date_as_int')

SIDEBAR_STYLE = {
    "margin-bottom": "2rem",
}

STYLE = {
    "margin-top": "2rem",
    "margin-left": "1rem",
    "margin-right": "1rem"
}

left_filter = html.Div(id='left_filter',
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
                           dbc.Col(
                               children=[
                                   html.H6('Choose a covid metric:'),
                                   dcc.Dropdown(
                                       kCovidDf.columns,
                                       id='covid-trend-selection',
                                       value='new_cases_smoothed_per_million',
                                       className='dbc',
                                       style=SIDEBAR_STYLE
                                   )]),
                           dbc.Col(
                               children=[
                                   html.H6('Choose a national response metric:'),
                                   dcc.Dropdown(
                                       kResponseOrdinalMeaning[['Name', 'Description']].rename(
                                           columns={'Name': 'value', 'Description': 'label'}).to_dict('records'),
                                       id='metric-selection',
                                       value='C1M_School closing',
                                       className='dbc',
                                       style=SIDEBAR_STYLE
                                   )]),
                       ])
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
corona_map = dbc.Card(id='corona_map',
                      children=[dcc.Loading(dcc.Graph(id='corona_map_graph'))]
                      )
corona_bubble = dbc.Card(id='corona_bubble',
                         children=[dcc.Graph(id='corona_bubble_graph')]
                         )
response_legend = html.Div(id='response_legend', )
corona_trend = dbc.Card(id='corona_trend',
                        children=[dcc.Loading(dcc.Graph(id='corona_trend_graph')), response_legend]
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
                                    children=[corona_map, corona_bubble],
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
#     Output('corona_bubble_graph', 'figure'),
#     [Input('location_selection', 'value'),
#      Input('date_range_picker', 'start_date'),
#      Input('date_range_picker', 'end_date'),
#      Input('metric-selection', 'value'),
#      Input('corona_trend_graph', 'hoverData')]
# )
def create_bubble_chart(dff, metric, max_x, max_y):
    fig = px.scatter(
        dff,
        x='new_cases_smoothed',
        y='new_deaths_smoothed',
        color='location',
        size='stringency_index',
        size_max=60,
        range_x=[0, max_x],
        range_y=[0, max_y]

    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(rangemode="tozero")
    return fig


@callback(
    Output('corona_bubble_graph', 'figure'),
    [Input('location_selection', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date'),
     Input('metric-selection', 'value'),
     Input('corona_trend_graph', 'hoverData')]
)
def update_bubble_chart(countries, start_date, end_date, metric, date_hover):
    if not countries:
        raise PreventUpdate
    if date_hover:
        date = date_hover['points'][0]['x']
    else:
        date = start_date

    filtered_df = merged_df[(merged_df['location'].isin(countries))]
    max_x = filtered_df.where(filtered_df['date'].between(start_date, end_date))['new_cases_smoothed'].max()
    max_y = filtered_df.where(filtered_df['date'].between(start_date, end_date))['new_deaths_smoothed'].max()
    filtered_df = filtered_df[(filtered_df['date'] == date)]
    return create_bubble_chart(filtered_df, metric, max_x, max_y)
