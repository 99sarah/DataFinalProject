from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate

education = pd.read_csv('../Data/states_all.csv', usecols=['STATE', 'YEAR', 'TOTAL_EXPENDITURE'])

resentEducation = education[(education['YEAR'] > 1992)]

app = Dash()
app.layout = html.Div([
    dcc.Dropdown(id='state-dropdown',
                 options=resentEducation['STATE'].apply(lambda state: state.capitalize()).unique()),
    dcc.Graph(id='education-line-chart')
])


@app.callback(
    Output('education-line-chart', 'figure'),
    Input('state-dropdown', 'value')
)
def update_education_graph(selected_state):
    if not selected_state:
        raise PreventUpdate
    fig = px.line(resentEducation[resentEducation['STATE'] == selected_state.upper()], x='YEAR', y='TOTAL_EXPENDITURE',
                  title=f'Expenditure in {selected_state}')
    return fig


if __name__ == '__main__':
    app.run(debug=True)
