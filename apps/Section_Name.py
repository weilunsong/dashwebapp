import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import plotly.graph_objects as go

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

df2 = pd.read_csv(DATA_PATH.joinpath('SpecialCampaign.csv'))

df2 = df2[['Section_Name', 'Completed', 'Project_Name']]
Completed = []
for i in df2.Completed:
    if i == True:
        Completed.append(1)
    else:
        Completed.append(0)
df2['Completed'] = Completed
df_sn = pd.DataFrame()
for i in list(df2.Project_Name.unique()):
    df = df2[df2['Project_Name'] == i]
    df = 1 - df.groupby(['Section_Name']).mean().round(2)
    df.reset_index(inplace=True)
    df['Project_Name'] = i
    df = df.rename({'Completed': 'Incomplete_Rate'}, axis=1)
    df_sn = df_sn.append(df)

df_sn['Incomplete_Rate'] = df_sn['Incomplete_Rate'].astype(float).map("{:.2%}".format)
dfs = df_sn

layout = html.Div([
    html.H1('', style={"textAlign": "center"}),
    html.Div([
        html.Pre(children="Special Campaign", style={"fontSize": "150%"}),
        dcc.Dropdown(id='Section_Name_select',
                     persistence=True,
                     persistence_type='session',
                     options=[{'label': i, 'value': i} for i in sorted(dfs.Project_Name.unique())],
                     value='OHIO Sign then Drive Campaign',
                     style={'width': '500px'})
    ]),
    dcc.Graph('Section_Name_graph', config={}),
    dcc.Graph('Section_Name_pie', config={})
])


@app.callback(Output('Section_Name_graph', 'figure'),
              [Input('Section_Name_select', 'value')
               ])
def update_graph(name):
    fig = go.Figure(data=[go.Table(header=dict(values=['Section_Name', 'Incomplete_Rate']),
                                   cells=dict(values=[dfs[dfs.Project_Name == name].Section_Name,
                                                      dfs[dfs.Project_Name == name].Incomplete_Rate]))
                          ])
    return fig


@app.callback(Output('Section_Name_pie', 'figure'),
              [Input('Section_Name_select', 'value')
               ])
def update_pie(name):
    df_pie = df2[df2['Project_Name'] == name]
    values = [len(df_pie[df_pie.Completed == 1]), len(df_pie[df_pie.Completed == 0])]
    names = ['Completed', 'Incompleted']
    fig = px.pie(values=values,
                 names=names,
                 title='Completed rate',
                 color_discrete_sequence=["lightsalmon", "cornflowerblue"])
    fig.update_traces(textinfo='percent+label')

    return fig
