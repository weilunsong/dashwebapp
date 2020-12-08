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

df3 = pd.read_csv(DATA_PATH.joinpath('Build.csv'))
df3 = df3[['Client_Name', 'SectionName', 'Completed', 'Brand']]
Completed = []
for i in df3.Completed:
    if i == True:
        Completed.append(1)
    else:
        Completed.append(0)
df3['Completed'] = Completed

df_brand = pd.DataFrame()
for i in list(df3.Brand.unique()):
    df = df3[df3['Brand'] == i]
    df = 1 - df.groupby(['Client_Name']).mean().round(2)
    df.reset_index(inplace=True)
    df['Brand'] = i
    df = df.rename({'Completed': 'Incomplete_Rate'}, axis=1)
    df_brand = df_brand.append(df)

df_brand['Incomplete_Rate'] = df_brand['Incomplete_Rate'].astype(float).map("{:.2%}".format)

dfb = df_brand

df_sc = pd.DataFrame()
for i in list(df3.Brand.unique()):
    df = df3[df3['Brand'] == i]
    df = 1 - df.groupby(['SectionName']).mean().round(2)
    df.reset_index(inplace=True)
    df['Brand'] = i
    df = df.rename({'Completed': 'Incomplete_Rate'}, axis=1)
    df_sc = df_sc.append(df)

df_sc['Incomplete_Rate'] = df_sc['Incomplete_Rate'].astype(float).map("{:.2%}".format)

sort_label_client = sorted(dfb.Brand.unique())
sort_label_client.insert(0, 'All')

layout = html.Div([
    html.H1('', style={"textAlign": "center"}),
    html.Div([
        html.Pre(children="Build", style={"fontSize": "150%"}),
        dcc.Dropdown(id='Client_Name_select',
                     persistence=True,
                     persistence_type='session',
                     options=[{'label': i, 'value': i} for i in sort_label_client],
                     value='All',
                     style={'width': '500px'})]),
    html.Div([
        dcc.Dropdown(id='Section_Name_select',
                     persistence=True,
                     persistence_type='session',
                     options=[{'label': i, 'value': i} for i in ['Client Name', 'Section Name']],
                     value='Client Name',
                     style={'width': '500px'})
    ]),
    dcc.Graph('Client_Name_graph', config={}),
    dcc.Graph('Client_Name_pie', config={})
])


@app.callback(Output('Client_Name_graph', 'figure'), [Input('Client_Name_select', 'value')],
              [Input('Section_Name_select', 'value')])
def update_client(client, section):
    if client == 'All':
        df = 1 - df3.groupby(['Brand']).mean().round(2)
        df.reset_index(inplace=True)
        df['Completed'] = df['Completed'].astype(float).map("{:.2%}".format)
        fig1 = go.Figure(data=[go.Table(header=dict(values=['Brand', 'Incomplete_Rate']),
                                        cells=dict(values=[df.Brand,
                                                           df.Completed]))])
        return fig1
    elif section == 'Client Name':
        fig2 = go.Figure(data=[go.Table(header=dict(values=['Client_Name', 'Incomplete_Rate']),
                                        cells=dict(values=[dfb[dfb.Brand == client].Client_Name,
                                                           dfb[dfb.Brand == client].Incomplete_Rate]))])
        return fig2
    elif section == 'Section Name':
        fig3 = go.Figure(data=[go.Table(header=dict(values=['Section_Name', 'Incomplete_Rate']),
                                        cells=dict(values=[df_sc[df_sc.Brand == client].SectionName,
                                                           df_sc[df_sc.Brand == client].Incomplete_Rate]))])
        return fig3


@app.callback(Output('Client_Name_pie', 'figure'),
              [Input('Client_Name_select', 'value')], [Input('Section_Name_select', 'value')])
def update_pie(client, section):
    if client == 'All':
        df_pie = df3
        values = [len(df_pie[df_pie.Completed == 1]), len(df_pie[df_pie.Completed == 0])]
        names = ['Completed', 'Incompleted']
        figp = px.pie(values=values,
                      names=names,
                      title='Completed rate',
                      color_discrete_sequence=["lightsalmon", "cornflowerblue"])
        figp.update_traces(textinfo='percent+label')
        return figp
    elif section == 'Client Name':
        fig1 = px.bar(dfb[dfb.Brand == client],
                      x='Client_Name',
                      y='Incomplete_Rate',
                      text=dfb[dfb.Brand == client].Incomplete_Rate)
        fig1.update_traces(textposition='outside')
        for data in fig1.data:
            data['width'] = 0.15
        return fig1

    elif section == 'Section Name':
        fig2 = px.bar(df_sc[df_sc.Brand == client],
                      x='SectionName',
                      y='Incomplete_Rate',
                      text=df_sc[df_sc.Brand == client].Incomplete_Rate)
        fig2.update_traces(textposition='outside')
        for data in fig2.data:
            data['width'] = 0.15
        return fig2
