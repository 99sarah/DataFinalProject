from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from data.covidData import kCovidDf

tab2 = dcc.Tab(
    label= 'Line chart',
    children=[
    'Tab 2',
    dcc.Dropdown(kCovidDf.continent.dropna().unique(), id='dropdown', value='Europe'),
    dcc.Graph(id='graph'),
])


@callback(
    Output('graph', 'figure'),
    Input('dropdown', 'value')
)
def update_graph(value):
    cov = kCovidDf[(kCovidDf.continent == value)]
    cov = cov.groupby('date').sum().reset_index()
    cov = cov[cov.total_cases != 0]
    return px.line(cov.dropna(), x='date', y='total_cases')
