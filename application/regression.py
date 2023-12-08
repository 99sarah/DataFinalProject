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
from data.covidData import kCovidDf, kResponseTrackerDf, kResponseOrdinalMeaning, label_map, get_label, STYLE, \
    SIDEBAR_STYLE, new_legend
import application.responseTracker

from sklearn import linear_model
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler

cov_df_grouped = kCovidDf.groupby(['iso_code', 'date']).sum().reset_index()
cov_df_grouped = cov_df_grouped[~(cov_df_grouped.iso_code.str.startswith('OWID', na=False))]

all_covid_metrics = ['new_cases_smoothed', 'icu_patients', 'reproduction_rate', 'hosp_patients', 'new_tests_smoothed',
                     'positive_rate', 'people_vaccinated']
all_response_metrics = ['StringencyIndex_Average', 'C1M_School closing', 'C2M_Workplace closing',
                        'C3M_Cancel public events',
                        'C4M_Restrictions on gatherings', 'C5M_Close public transport', 'C6M_Stay at home requirements',
                        'C7M_Restrictions on internal movement', 'C8EV_International travel controls',
                        'E1_Income support', 'H1_Public information campaigns', 'H2_Testing policy',
                        'H3_Contact tracing', 'H4_Emergency investment in healthcare', 'H7_Vaccination policy',
                        'H8M_Protection of elderly people']

left_filter = dbc.Card(html.Div(id='regression_left_filter',
                                style=STYLE,
                                children=[
                                    dbc.Col(
                                        children=[
                                            html.H6('Choose countries:'),
                                            dcc.Dropdown(
                                                kResponseTrackerDf.CountryName.unique(),
                                                id='regression_location_selection',
                                                value='Germany',
                                                className='dbc',
                                                style=SIDEBAR_STYLE
                                            )]),
                                    dbc.Col(
                                        children=[
                                            html.H5('Select metrics you want to predict with',
                                                    style={"margin-bottom": "1rem"}),
                                            html.H6('Covid trend metrics:'),
                                            dcc.Dropdown(
                                                # all_covid_metrics,
                                                options=label_map(all_covid_metrics),
                                                id='regression_covid_selection',
                                                value=[all_covid_metrics[0]],
                                                className='dbc',
                                                style={"margin-bottom": "0.5rem", },
                                                multi=True
                                            ),
                                            html.H6('policy response metrics:'),
                                            dcc.Dropdown(
                                                # all_response_metrics,
                                                options=label_map(kResponseOrdinalMeaning['Name']) +
                                                        [{'label': 'Stringency index',
                                                          'value': 'StringencyIndex_Average'}],
                                                id='regression_response_selection',
                                                value=['C1M_School closing'],
                                                className='dbc',
                                                style=SIDEBAR_STYLE,
                                                multi=True
                                            ),
                                        ]),
                                ]))

regression_chart = dbc.Card(
    id="lasso_regression",
    children=[
        dcc.Graph(
            id='regression_line_chart'
        )
    ]
)
lasso_pie = dbc.Card(
    id="lasso_pie",
    children=[
        dcc.Graph(
            id='pie_chart'
        )
    ]
)

regression_tab = dcc.Tab(
    label='Prediction',
    children=[
        html.H1('Prediction of new deaths', style={'textAlign': 'center'}),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[left_filter],
                    width=3
                ),
                dbc.Col(
                    children=[
                        regression_chart,
                        dbc.Row(
                            children=[
                                dbc.Col(html.Div(children=[
                                    html.H6('Prediction accuracy calculated with RMLSE: '),
                                    html.Br(),
                                    html.Center(html.H5(id='rmlse_score_display')),
                                ],
                                    style=STYLE
                                ), width=4),
                                dbc.Col(lasso_pie, width=8)
                            ],
                        )
                    ],
                    width=9
                )
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(width=8),
                dbc.Col(
                    children=[

                    ],
                    width=4
                ), ]
        ),
    ])


def rss(y, y_hat):
    return ((y - y_hat) ** 2).sum()
    pass


def score(y_pred, y_true):
    # source: https://medium.com/analytics-vidhya/root-mean-square-log-error-rmse-vs-rmlse-935c6cc1802a
    error = np.square(np.log10(y_pred + 1) - np.log10(y_true + 1)).mean() ** 0.5
    score = 1 - error
    return score


def print_nonzero_weights(model, feature_list):
    dataframe = pd.DataFrame()
    dataframe["features"] = feature_list
    dataframe["weight"] = model.coef_
    print(dataframe[dataframe["weight"] != 0])
    return dataframe[dataframe["weight"] != 0]


@callback(
    [Output('regression_line_chart', 'figure'),
     Output('pie_chart', 'figure'),
     Output('rmlse_score_display', 'children')],
    [Input('regression_location_selection', 'value'),
     Input('regression_covid_selection', 'value'),
     Input('regression_response_selection', 'value')]
)
def perform_lasso_regression(country, covid_metrics, response_metrics):
    if not country or (not covid_metrics and not response_metrics):
        raise PreventUpdate
    if not covid_metrics:
        covid_metrics = []
    if not response_metrics:
        response_metrics = []
    regression_metric = 'new_deaths_smoothed'

    merge_covid_df = pd.DataFrame()
    merge_covid_df[['date', regression_metric] + covid_metrics] = kCovidDf.query('location == @country')[
        ['date', regression_metric] + covid_metrics]
    merge_covid_df.set_index('date', inplace=True)

    merge_response_df = pd.DataFrame()
    merge_response_df[['date'] + response_metrics] = kResponseTrackerDf.query('CountryName == @country')[
        ['Date'] + response_metrics]
    merge_response_df.set_index('date', inplace=True)

    all_regression_columns = pd.concat([merge_covid_df, merge_response_df], axis=1, join='inner')
    all_regression_columns.fillna(0, inplace=True)

    all_features = covid_metrics
    all_features += response_metrics

    # rescales all feature columns
    all_regression_columns[all_features] = StandardScaler().fit_transform(all_regression_columns[all_features])

    train_data = all_regression_columns.sample(frac=0.6)
    valid_and_test = all_regression_columns.drop(train_data.index)
    valid_data = valid_and_test.sample(frac=0.5)
    test_data = valid_and_test.drop(valid_data.index)

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

    model = linear_model.Lasso(alpha=best_lambda, max_iter=100000)
    model.fit(train_data[all_features], train_data[regression_metric])
    prediction_val = model.predict(test_data[all_features])
    np.clip(prediction_val, 0, None, out=prediction_val)
    non_zero_df = print_nonzero_weights(model, all_features)

    print(f"Intercept: {model.intercept_}")
    cur_rss = rss(test_data[regression_metric], prediction_val)
    rmlse_score = (score(test_data[regression_metric], prediction_val) * 100).round(2)
    print(cur_rss)

    test_data['prediction'] = prediction_val

    test_data.sort_index(inplace=True)
    train_data.sort_index(inplace=True)

    reg_fig = go.Figure()
    reg_fig.add_trace(
        go.Scatter(x=train_data.index, y=train_data[regression_metric], mode='markers', name='Training data set'))
    reg_fig.add_trace(go.Scatter(x=test_data.index, y=test_data[regression_metric], text='response', mode='markers',
                                 name='Test data set'))
    reg_fig.add_trace(go.Scatter(x=test_data.index, y=test_data['prediction'], text='prediction', name='Prediction'))
    reg_fig.update_layout(xaxis_title='Time',
                          yaxis_title=get_label(regression_metric)
                          )

    pie_fig = update_pie_chart(non_zero_df)

    return [reg_fig, pie_fig, f'{rmlse_score}%']


def update_pie_chart(non_zero_df):
    new_df = non_zero_df
    new_df['weight'] = new_df['weight'].apply(abs)
    fig = px.pie(
        new_df,
        values='weight',
        names='features',
        title='Influence of the metrics on the prediction'
    )
    fig = new_legend(fig=fig, names=new_df['features'])
    return fig
