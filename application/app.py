from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from worldwide import worldwideTab
from regression import regression_tab
from analysis import analysisTab

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
external_stylesheets = [dbc.themes.DARKLY, dbc_css]
app = Dash(__name__, external_stylesheets=external_stylesheets)
load_figure_template("DARKLY")

app.layout = html.Div([
    dcc.Tabs(
        value='worldwideTab',
        children=[
            worldwideTab,
            analysisTab,
            regression_tab,
        ], className='dbc'),
])

if __name__ == '__main__':
    app.run(debug=False)
