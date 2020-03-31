import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import callbacks
from app import app
from layout import second_tab_layout


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return second_tab_layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True, port=5000)
