import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

education = pd.read_csv("../Data/states_all.csv", usecols=["STATE", "YEAR", "TOTAL_EXPENDITURE"])


app = Dash(__name__)

app.layout = html.Div([
    "Select a State",
    dcc.Dropdown(
        options=education["STATE"].apply(lambda state: state.capitalize()).unique(),
        id="dropdown"
    ),
    dcc.Graph(id="graph")
])

@app.callback(
    Output("graph","figure"),
    Input("dropdown", "value")
)
def update_graph(state):
    if not state:
        raise PreventUpdate
    new_df = education.query(f"STATE == '{state.upper()}' & YEAR > 1992")
    figure = px.line(new_df, x="YEAR", y="TOTAL_EXPENDITURE", title=f"Expenditure in {state.capitalize()}")
    return figure

#df = education.query("STATE == 'WASHINGTON' & YEAR > 1992")

#px.line(df, x="YEAR", y="TOTAL_EXPENDITURE", title="Expenditure in Washington")



if __name__ == '__main__':
    app.run(debug=True)