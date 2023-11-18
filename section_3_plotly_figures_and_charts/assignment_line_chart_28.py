from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

spain_skiers = pd.read_csv("../Data/spanish_skiers.csv")

print(spain_skiers.head())

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div(
    dcc.Graph(
        figure = px.line(spain_skiers, x='Year', y='Percent_Skiers', labels={'Percent_Skiers': 'Percentage of spaniards that skied'})
    )
)

if __name__ == '__main__':
    app.run(debug=True)
