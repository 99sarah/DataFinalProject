import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


spain_skiers = pd.read_csv("../Data/spanish_skiers.csv")

external_stylesheets = [dbc.themes.SLATE]
app = Dash(__name__, external_stylesheets=external_stylesheets)
load_figure_template("SLATE")


app.layout = html.Div([
    html.H1('Hallo'),
    dcc.Graph(
        figure=px.line(
            spain_skiers, x="Year",
            y="Percent_Skiers",
            title="Percent of Spanish Who Skied Each Year",
            #color_discrete_sequence=px.colors.qualitative.Dark2
        )
    )
])

if __name__ == '__main__':
    app.run(debug=True)