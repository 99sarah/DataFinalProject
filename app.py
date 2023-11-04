from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
])


# @app.callback(
#     Output('', ''),
#     Input('', '')
# )
# def country_picker(state):
#     if not country:
#         raise PreventUpdate
#     return f'I live in {state}'


if __name__ == '__main__':
    app.run(debug=True)
