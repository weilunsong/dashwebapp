import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
import numpy as np
from app import app
import plotly.graph_objects as go

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

df1 = pd.read_csv(DATA_PATH.joinpath('Tier3.csv'))
df1 = df1[['OEM', 'Completed', 'Project_Name']]
Completed = []
for i in df1.Completed:
    if i == True:
        Completed.append(1)
    else:
        Completed.append(0)
df1['Completed'] = Completed

df_oem = pd.DataFrame()
for i in list(df1.Project_Name.unique()):
    df = df1[df1['Project_Name'] == i]
    df = 1 - df.groupby(['OEM']).mean().round(2)
    df.reset_index(inplace=True)
    df['Project_Name'] = i
    df = df.rename({'Completed': 'Incomplete_Rate'}, axis=1)
    df_oem = df_oem.append(df)

df_oem['Incomplete_Rate'] = df_oem['Incomplete_Rate'].astype(float).map("{:.2%}".format)

dfo = df_oem

layout = html.Div([
    html.H1('', style={"textAlign": "center"}),
    html.Div([
        html.Pre(children="Tier3", style={"fontSize": "150%"}),
        dcc.Dropdown(id='OEM_select',
                     persistence=True,
                     persistence_type='session',
                     options=[{'label': i, 'value': i} for i in sorted(dfo.Project_Name.unique())],
                     value='December National Incentives',
                     style={'width': '500px'})
    ]),
    dcc.Graph('OEM_graph', config={}),
    dcc.Graph('OEM_pie', config={})
])


@app.callback(Output('OEM_graph', 'figure'), [Input('OEM_select', 'value')])
def update_graph(name):
    fig = go.Figure(data=[go.Table(header=dict(values=['OEM', 'Incomplete_Rate']),
                                   cells=dict(values=[dfo[dfo.Project_Name == name].OEM,
                                                      dfo[dfo.Project_Name == name].Incomplete_Rate]))
                          ])
    return fig


@app.callback(Output('OEM_pie', 'figure'), [Input('OEM_select', 'value')])
def update_pie(name):
    df_pie = df1[df1['Project_Name'] == name]
    values = [len(df_pie[df_pie.Completed == 1]), len(df_pie[df_pie.Completed == 0])]
    names = ['Completed', 'Incompleted']
    fig = px.pie(values=values,
                 names=names,
                 title='Completed rate',
                 color_discrete_sequence=["lightsalmon", "cornflowerblue"])
    fig.update_traces(textinfo='percent+label')
    return fig
