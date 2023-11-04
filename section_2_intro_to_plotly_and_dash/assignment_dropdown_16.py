from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

app = Dash(__name__)

app.layout = html.Div([
    'Select a State to Analyze: ',
    dcc.Dropdown(
        id='state-dropdown',
        options=['California', 'Oregon', 'Washington']
    ),
    html.Div(id='state-output')
])


@app.callback(
    Output('state-output', 'children'),
    Input('state-dropdown', 'value')
)
def update_output_div(state):
    if not state:
        raise PreventUpdate
    return f'State selected: {state}'


if __name__ == '__main__':
    app.run(debug=True)
