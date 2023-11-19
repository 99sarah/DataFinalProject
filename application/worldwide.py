from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np

from data.covidData import kCovidDf

worldwideTab = dcc.Tab(label='Covid-19 worldwide ',
                       value='worldwideTab',
                       children=[
                           html.H1(children='Covid-19 worldwide',
                                   style={'textAlign': 'center'}),
                           dcc.DatePickerRange(
                               id='date_picker',
                               start_date=kCovidDf['date'].min(),
                               end_date=kCovidDf['date'].max(),
                               className='dbc'
                           ),
                           dcc.Graph(id='graph-content')
                       ])


@callback(
    Output('graph-content', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)
def update_graph(start, end):
    metric = 'new_cases_smoothed_per_million'
    cov_df_in_range = kCovidDf[kCovidDf['date'].between(start, end)]
    cov_df_grouped = cov_df_in_range.groupby(['iso_code', 'date']).sum().reset_index()
    # cov_df_grouped = cov_df_in_range[~(cov_df_in_range.iso_code.str.startswith('OWID', na=False))]
    # cov_df_grouped.iso_code = cov_df_grouped.iso_code.str.replace("OWID_", "")
    quantile = cov_df_grouped[metric].quantile(0.99)
    return px.choropleth(cov_df_grouped,
                         locations='iso_code',
                         color=metric,
                         locationmode='ISO-3',
                         animation_frame=cov_df_grouped['date'].dt.date,
                         range_color=(cov_df_grouped[metric].min(),
                                      quantile),
                         color_continuous_scale=px.colors.sequential.solar,


                         )
