from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from application.responseTracker import responseTrackerTab
from data.covidData import name_to_iso, iso_to_name
from tab1 import tab1
from tab2 import tab2
from correlation import correlationTab

print(name_to_iso['Germany'])
print(iso_to_name['OWID_EUR'])

app = Dash(__name__)

app.layout = html.Div([
    dcc.Tabs([
        tab1,
        tab2,
        correlationTab,
        responseTrackerTab
    ]),
])

if __name__ == '__main__':
    app.run(debug=True)
