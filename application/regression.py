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

left_filter = html.Div(id='regression_left_filter',
                       style=STYLE,
                       children=[
                           dbc.Col(
                               children=[
                                   html.H6('Pick countries:'),
                                   dcc.Dropdown(
                                       kResponseTrackerDf.CountryName.unique(),
                                       id='regression_location_selection',
                                       value=['Germany'],
                                       multi=True,
                                       className='dbc',
                                       style=SIDEBAR_STYLE
                                   )]),
                       ])

regression_chart = dbc.Card(
    id="lasso_regression",
    children=[
        dcc.Graph(
            id='regression_line_chart'
        )
    ]
)

regression_tab = dcc.Tab(
    label='Regression',
    children=[
        html.H1('Regression of new cases', style={'textAlign': 'center'}),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[left_filter],
                    width=2
                ),
                dbc.Col(
                    children=[regression_chart],
                    width=10
                )]
        ),
    ])


@callback(
    [Output('regression_line_chart', 'figure')],
    [Input('regression_location_selection', 'value')]
)
def perform_lasso_regression(country):
    return px.line(kCovidDf.query('location == @country'), x='date', y='new_cases_smoothed')
