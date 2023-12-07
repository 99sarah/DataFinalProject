from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from data.covidData import kCovidDf, SIDEBAR_STYLE, STYLE, label_map, get_label

map_metrics = ['new_cases_smoothed_per_million',
               'new_deaths_smoothed_per_million',
               'people_vaccinated_per_hundred',
               'total_cases_per_million']

map_sidebar = dbc.Card(html.Div(
    style=STYLE,
    children=[
        html.H6('Choose a time period'),
        dcc.DatePickerRange(
            id='date_picker',
            start_date='2020-03-01',
            end_date='2022-12-31',
            className='dbc',
            style=SIDEBAR_STYLE
        ),
        html.H6('Choose a daily metric'),
        dcc.Dropdown(
            id='map_metric_dropdown',
            options=label_map(map_metrics),
            value='new_cases_smoothed_per_million',
            className='dbc',
            style=SIDEBAR_STYLE
        )
    ],
)
)

map_content = dbc.Card(
    id="map-content", children=[
        dcc.Loading(dcc.Graph(id='map-graph'))
    ],
)

worldwideTab = dcc.Tab(label='Covid-19 worldwide ',
                       value='worldwideTab',
                       children=[

                           dbc.Col(
                               children=[
                                   html.H1(children='Daily situation of covid-19 worldwide',
                                           style={'textAlign': 'center'}),
                                   dbc.Row(
                                       [
                                           dbc.Col(map_sidebar, width=3),
                                           dbc.Col(map_content, width=9)
                                       ],
                                       style=STYLE
                                   ),
                               ]
                           )

                       ],
                       )


@callback(
    Output('map-graph', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('map_metric_dropdown', 'value')]
)
def update_map(start, end, map_metric):
    if not start or not end or not map_metric:
        raise PreventUpdate
    metric = map_metric
    cov_df_in_range = kCovidDf[kCovidDf['date'].between(start, end)]
    cov_df_grouped = cov_df_in_range.groupby(['iso_code', 'date']).sum().reset_index()
    # cov_df_grouped = cov_df_in_range[~(cov_df_in_range.iso_code.str.startswith('OWID', na=False))]
    # cov_df_grouped.iso_code = cov_df_grouped.iso_code.str.replace("OWID_", "")
    quantile = cov_df_grouped[map_metric].quantile(0.99)
    fig = px.choropleth(cov_df_grouped,
                        locations='iso_code',
                        color=map_metric,
                        locationmode='ISO-3',
                        animation_frame=cov_df_grouped['date'].dt.date,
                        animation_group='iso_code',
                        hover_name='location',
                        range_color=(cov_df_grouped[metric].min(),
                                     quantile),
                        color_continuous_scale=px.colors.sequential.solar,
                        height=800,
                        #width=1500,
                        )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(coloraxis_colorbar_title_text=get_label(metric))
    fig.layout.sliders[0].currentvalue.prefix = 'Date='
    return fig
