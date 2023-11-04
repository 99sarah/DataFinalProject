import seaborn as sns
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

app = Dash(__name__)

df = sns.load_dataset("anscombe")

app.layout = html.Div([
    html.H3("Anscombe's Quartet"),
    dcc.Dropdown(
        id="dropdown",
        options=df["dataset"].unique()
    ),
    dcc.Graph(id="visual")
])


@app.callback(
    Output("visual", "figure"),
    Input("dropdown","value")
)
def anscombes_scatter(dataset):
    figure = px.scatter(
        df.query(f"dataset == '{dataset}'"),
        x="x",
        y="y"
    )
    return figure

if __name__ == '__main__':
    app.run(debug=True)