import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import OEM, Section_Name, Client_Name

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Tier3 | ', href='/apps/Tier3'),
        dcc.Link('Special Campaign | ', href='/apps/Special_Campaign'),
        dcc.Link('Build', href='/apps/Build')
    ], className="row"),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/Tier3':
        return OEM.layout
    if pathname == '/apps/Special_Campaign':
        return Section_Name.layout
    if pathname == '/apps/Build':
        return Client_Name.layout
    else:
        return OEM.layout


if __name__ == '__main__':
    app.run_server(debug=False)


