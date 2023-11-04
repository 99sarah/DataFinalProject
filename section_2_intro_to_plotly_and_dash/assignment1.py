from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children="Select a State to Analyze"),
    dcc.Dropdown(
        options=["California", "Oregon", "Washington"],
        id="state-input",
    ),
    html.H3(id="state-output")
])


@app.callback(
    Output("state-output", "children"),
    Input("state-input", "value")
)
def state_picker(value):
    if not value:
        raise PreventUpdate
    return f"State Selected: {value}"


if __name__ == '__main__':
    app.run(debug=True)
