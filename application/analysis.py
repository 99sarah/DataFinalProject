from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import json
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from matplotlib.dates import date2num, num2date
from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning, kCovid_Response, date_format, \
    kCovidDf_without_owid, get_label, label_map, STYLE, SIDEBAR_STYLE
import application.responseTracker

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
                                            start_date='2020-03-01',
                                            end_date='2022-12-31',
                                            className='dbc',
                                            style=SIDEBAR_STYLE
                                        )]),
                                    dbc.Col(
                                        children=[
                                            html.H6('Select countries:'),
                                            dcc.Dropdown(
                                                kResponseTrackerDf.CountryName.unique(),
                                                id='location_selection',
                                                value=['Germany', 'Norway', 'Sweden'],
                                                multi=True,
                                                className='dbc',
                                                style=SIDEBAR_STYLE
                                            )]),

                                ]))
top_filter = dbc.Card(id='top_filter')
corona_map = dbc.Card(id='corona_map',
                      children=[dcc.Loading(dcc.Graph(id='corona_map_graph'))]
                      )

response_legend = html.Div(id='response_legend', )
response_dropdown = dbc.Row(
    children=[dbc.Col(
        children=[
            html.H6('Choose a covid metric:'),
            dcc.Dropdown(
                # kCovidDf.columns,
                options=label_map(kCovidDf.columns),
                id='covid-trend-selection',
                value='new_cases_smoothed_per_million',
                className='dbc',
            ),
        ],
        style=STYLE,
        width=5
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
            style=STYLE,
            width=6
        ), ]
)
corona_trend = dbc.Card(id='corona_trend',
                        children=[
                            response_dropdown,
                            dcc.Loading(dcc.Graph(id='corona_trend_graph')),
                            response_legend
                        ]
                        )
radio_button = dbc.Row(children=[
    dbc.RadioItems(
        id='radio_item',
        options=['absolut', 'relative (per million)'],
        value='absolut',
    )
])
corona_bubble = dbc.Card(id='corona_bubble',
                         children=[dcc.Graph(id='corona_bubble_graph'),
                                   radio_button]
                         )
stringency_bar = dbc.Card(
    id='stringency_bar',
    children=[dcc.Graph(id='stringency_bar_chart'),
              html.Div(f'The stringency index is a composite measure based on nine response indicators '
                       f'rescaled to a value from 0 to 100 (100 = strictest).', style=STYLE)]
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
    map_metric = 'new_cases'
    # filter data between given dates
    cov_df_in_range = kCovidDf_without_owid[kCovidDf_without_owid['date'].between(start_date, end_date)]
    cov_df = cov_df_in_range[['iso_code', 'location', map_metric]]
    cov_df = cov_df.groupby(['iso_code', 'location']).sum().reset_index()
    # show map
    fig = px.choropleth(cov_df,
                        locations='iso_code',
                        color=map_metric,
                        locationmode='ISO-3',
                        scope=continent,
                        hover_name='location',
                        range_color=(cov_df[map_metric].min(),
                                     cov_df[map_metric].max()),
                        color_continuous_scale=px.colors.sequential.solar,
                        title=f'New Cases between {pd.to_datetime(start_date).strftime(date_format)} and {pd.to_datetime(end_date).strftime(date_format)}'
                        )
    fig.update_layout(margin=dict(t=45, r=2, l=5, b=20))
    fig.update_layout(coloraxis=dict(colorbar=dict(orientation='h', y=-0.15)))
    fig.update_layout(coloraxis_colorbar_title_text=get_label(map_metric))
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


def create_bubble_chart(dff, x_metric, y_metric, max_x, max_y, title):
    fig = px.scatter(
        dff,
        x=x_metric,
        y=y_metric,
        color='location',
        size_max=20,
        range_x=[0, max_x],
        range_y=[0, max_y],
        title=title,
    )
    fig.update_xaxes(rangemode="tozero", title=get_label(x_metric))
    fig.update_yaxes(rangemode="tozero", title=get_label(y_metric))
    fig.update_traces(marker={'size': 20})
    fig.update_legends(title=get_label('location'))

    return fig


@callback(
    [Output('corona_bubble_graph', 'figure'),
     Output('stringency_bar_chart', 'figure')],
    [Input('location_selection', 'value'),
     Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date'),
     Input('corona_trend_graph', 'hoverData'),
     Input('radio_item', 'value')
     ]
)
def update_bubble_bar_chart(countries, start_date, end_date, date_hover, metric_type):
    if not countries:
        raise PreventUpdate
    if date_hover:
        date = date_hover['points'][0]['x']
    else:
        date = start_date

    if metric_type == 'absolut':
        x_column = 'new_cases_smoothed'
        y_column = 'new_deaths_smoothed'
    else:
        x_column = 'new_cases_smoothed_per_million'
        y_column = 'new_deaths_smoothed_per_million'

    filtered_df = kCovid_Response[(kCovid_Response['location'].isin(countries))]
    max_x = filtered_df.where(filtered_df['date'].between(start_date, end_date))[x_column].max()
    max_y = filtered_df.where(filtered_df['date'].between(start_date, end_date))[y_column].max()
    filtered_df = filtered_df[(filtered_df['date'] == date)]
    bubble_title = f'Comparison of new cases and new deaths on {pd.to_datetime(date).strftime(date_format)}'
    bar_title = f'Stringency index on {pd.to_datetime(date).strftime(date_format)}'

    return [create_bubble_chart(filtered_df, x_column, y_column, max_x, max_y, bubble_title),
            create_bar_chart(filtered_df, bar_title)]


def create_bar_chart(dff, title):
    fig = px.bar(
        dff,
        x='location',
        y='stringency_index',
        range_y=[0, 100],
        title=title,
        color='location'
    )
    fig.update_yaxes(title=get_label('stringency_index'))
    fig.update_xaxes(title=get_label('location'))
    fig.update_legends(title=get_label('location'))
    return fig
