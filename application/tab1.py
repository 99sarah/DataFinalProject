from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from data.covidData import kCovidDf

tab1 = dcc.Tab(
    label= 'Line chart',
    children = [
    'Line Chart',
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(kCovidDf.iso_code.unique(), value='DEU', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = kCovidDf[kCovidDf.iso_code == value]
    return px.scatter(dff, x='people_vaccinated', y='icu_patients')
