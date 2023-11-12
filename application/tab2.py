from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

covidDf = pd.read_csv('./data/owid-covid-data.csv')


tab2 = dcc.Tab(children=[
    'Tab 2',
    dcc.Dropdown(covidDf.continent.dropna().unique(), id='dropdown'),
    dcc.Graph(id='graph'),
])


@callback(
    Output('graph', 'figure'),
    Input('dropdown', 'value')
)
def update_graph(value):
    cov = covidDf[(covidDf.continent == value)]
    cov = cov.groupby('date').sum().reset_index()
    cov = cov[cov.total_cases != 0]
    return px.line(cov.dropna(), x='date', y='total_cases')
