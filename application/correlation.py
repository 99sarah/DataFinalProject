from data.covidData import kCovidDf
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data.covidData import kCovidDf


def neutraliseIrrelevantData(x):
    if x > 0.985 or x < 0.65:
        return None
    return x


correlationMatrix = kCovidDf.corr(numeric_only=True).abs().map(neutraliseIrrelevantData)
correlationMatrixDEU = kCovidDf[kCovidDf['iso_code'] == 'DEU'].corr(numeric_only=True).abs().map(
    neutraliseIrrelevantData)

correlationTab = dcc.Tab(
    label='Correlation heatmap',
    children=[
        'correlation',
        dcc.Graph(figure=go.Figure(
            data=go.Heatmap(z=correlationMatrix, x=correlationMatrix.columns, y=correlationMatrix.index),
        ).update_layout(
            height=1400
        ), ),
        'correlations Germany',
        dcc.Graph(figure=go.Figure(
            data=go.Heatmap(z=correlationMatrixDEU, x=correlationMatrix.columns, y=correlationMatrix.index),
        ).update_layout(
            height=1400
        ), ),
    ])
