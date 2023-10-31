from dash import Dash, html, dash_table, dcc
import plotly.express as px
import pandas as pd

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(
        html.H1('This is section 2', style={'textAlign': 'center', 'color': '#7FDBFF'})
    ),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.histogram(df, x='continent', y='lifeExp', histfunc='avg'))
])

if __name__ == '__main__':
    app.run(debug=True)