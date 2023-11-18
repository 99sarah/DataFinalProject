from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from tab1 import tab1
from tab2 import tab2



app = Dash(__name__)

app.layout = html.Div([
    dcc.Tabs([
        tab1,
        tab2,
    ]),
])

if __name__ == '__main__':
    app.run(debug=True)
