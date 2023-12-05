from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from matplotlib.dates import date2num, num2date
from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning
import application.responseTracker

from sklearn import linear_model
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

cov_df_grouped = kCovidDf.groupby(['iso_code', 'date']).sum().reset_index()
cov_df_grouped = cov_df_grouped[~(cov_df_grouped.iso_code.str.startswith('OWID', na=False))]

# date_converter = pd.DataFrame()
# date_converter['value'] = kCovidDf['date']
# date_converter['key'] = date_converter['value'].astype(np.int64)
# date_converter.set_index('date_as_int')

SIDEBAR_STYLE = {
    "margin-bottom": "2rem",
}

STYLE = {
    "margin-top": "2rem",
    "margin-left": "1rem",
    "margin-right": "1rem"
}

left_filter = html.Div(id='regression_left_filter',
                       style=STYLE,
                       children=[
                           dbc.Col(
                               children=[
                                   html.H6('Pick countries:'),
                                   dcc.Dropdown(
                                       kResponseTrackerDf.CountryName.unique(),
                                       id='regression_location_selection',
                                       value='Germany',
                                       className='dbc',
                                       style=SIDEBAR_STYLE
                                   )]),
                       ])

regression_chart = dbc.Card(
    id="lasso_regression",
    children=[
        dcc.Graph(
            id='regression_line_chart'
        )
    ]
)

regression_tab = dcc.Tab(
    label='Regression',
    children=[
        html.H1('Regression of new cases', style={'textAlign': 'center'}),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[left_filter],
                    width=2
                ),
                dbc.Col(
                    children=[regression_chart],
                    width=10
                )]
        ),
    ])


def rss(y, y_hat):
    return ((y - y_hat) ** 2).sum()
    pass


def print_nonzero_weights(model, feature_list):
    dataframe = pd.DataFrame()
    dataframe["features"] = feature_list
    dataframe["weight"] = model.coef_
    print(dataframe[dataframe["weight"] != 0])


@callback(
    Output('regression_line_chart', 'figure'),
    Input('regression_location_selection', 'value')
)
def perform_lasso_regression(country):
    regression_metric = 'new_deaths_smoothed'
    all_features = ['new_cases_smoothed', 'icu_patients', 'reproduction_rate', 'people_vaccinated']
    country_df = kCovidDf.query('location == @country')[all_features + [regression_metric, 'date']]
    print(country_df.isna().sum())
    country_df.fillna(0, inplace=True)
    country_df.set_index(['date'], inplace=True)

    train_data = country_df.sample(frac=0.6, random_state=12)
    valid_and_test = country_df.drop(train_data.index)
    valid_data = valid_and_test.sample(frac=0.5, random_state=62)
    test_data = country_df.drop(valid_data.index)

    penalties = np.logspace(-4, 3, num=30)
    best_lambda = None
    for l in penalties:
        model = linear_model.Lasso(alpha=l, max_iter=100000)
        model.fit(train_data[all_features], train_data[regression_metric])

        # validDataAll = valid_data[all_features]
        prediction_val = model.predict(valid_data[all_features])

        cur_rss = rss(valid_data[regression_metric], prediction_val)
        if best_lambda is None or cur_rss < best_lambda:
            best_lambda = l
        pass

    model = linear_model.Lasso(alpha=best_lambda, max_iter=1000000)
    model.fit(train_data[all_features], train_data[regression_metric])
    #print_nonzero_weights(model, all_features)

    print(f"Intercept: {model.intercept_}")

    valid_data['prediction'] = prediction_val

    valid_data.sort_index(inplace=True)
    train_data.sort_index(inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_data.index, y=train_data[regression_metric], text='train'))
    fig.add_trace(go.Scatter(x=valid_data.index, y=valid_data['prediction'], text='prediction'))
    fig.add_trace(go.Scatter(x=valid_data.index, y=valid_data[regression_metric], text='validation'))

    return fig
