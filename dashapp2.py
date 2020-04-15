# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 15:42:11 2020

@author: CBN
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import date

#%% This week
weekNumber = date.today().isocalendar()[1]

#%% Define stylesheets and app server
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#%% Load dataframe
df = pd.read_csv('Dashboard_input_v2.csv', sep=';')

#%% Prepare dataframe for werknemer data
# Create dataframe for hours per week per werknemer
df_wn_week = df.drop(columns=['Projectnummer', 'Projectnaam', 'Taken', 'Projectleider', 'Status', 'Target'])
df_wn_week = df_wn_week[df_wn_week['Werknemer'].notna()]
df_wn_week = df_wn_week.groupby(['Werknemer', 'Vakgroep']).sum()

# Create dataframe for target hours per week per werknemer
df_wn_target = df.loc[:, ['Werknemer', 'Vakgroep', 'Target']]
df_wn_target = df_wn_target.groupby(['Werknemer', 'Vakgroep']).mean()
df_wn_target = df_wn_target.reset_index()

# Calculate percentage
df_wn_tot = pd.merge(df_wn_week, df_wn_target, on=['Werknemer', 'Vakgroep'])
df_wn_per = df_wn_tot.iloc[:, 2:54].div(df_wn_tot['Target'], axis= 'index')
df_wn_per['Werknemer'] = df_wn_tot['Werknemer']
df_wn_per['Vakgroep'] = df_wn_tot['Vakgroep']
df_wn_per = df_wn_per.melt(id_vars=['Werknemer', 'Vakgroep'], var_name='Week')
df_wn_per['Bezetting'] = df_wn_per['value']*100
df_wn_per = df_wn_per.drop(['value'], axis=1)

#Define indicator
wn_indicator = df_wn_per['Werknemer'].unique()

#%% Prepare dataframe for vakgroep data
# Create column for bezetting per vakgroep
df_vg_per = df_wn_per
df_vg_per = df_vg_per.groupby(['Vakgroep', 'Week'], as_index=False)['Bezetting'].mean()
df_vg_per['Week'] = df_vg_per['Week'].astype(int)
df_vg_per = df_vg_per.sort_values(by='Week', ascending=True)

#Define indicator
vg_indicator = df_vg_per['Vakgroep'].unique()

#%% Prepare dataframe for total data
# Create column for total bezetting
df_tot = df_vg_per
df_tot = df_tot.groupby(['Week'], as_index=False)['Bezetting'].mean()
df_tot['Week'] = df_tot['Week'].astype(int)
df_tot = df_tot.sort_values(by='Week', ascending=True)

#%% Prepare dataframe for project data
df_proj = df.drop(columns=['Vakgroep', 'Projectnummer', 'Taken', 'Projectleider', 'Status'])
df_proj = df_proj[df_proj['Werknemer'].notna()]
df_proj_week = df_proj.groupby(['Werknemer', 'Projectnaam']).sum()

df_proj_abs = df_proj.iloc[:, 3:55]
df_proj_abs = df_proj_abs.fillna(0)
df_proj_abs['Werknemer'] = df_proj['Werknemer']
df_proj_abs['Projectnaam'] = df_proj['Projectnaam']
df_proj_abs = df_proj_abs[df_proj_abs['Projectnaam'].notna()]
df_proj_abs = df_proj_abs.melt(id_vars=['Werknemer', 'Projectnaam'], var_name='Week', value_name='Uren')
df_proj_abs = df_proj_abs.groupby(['Werknemer', 'Projectnaam'], as_index=False).sum()

#%% Define app layout
app.layout = html.Div([
    #Set upper row with dashboard title
    html.Div([
        html.H1('Capaciteitsplanning BU Water'),
        html.Details([
            html.Summary('Uitleg over het dashboard'),
            dcc.Markdown('''Dit dashboard laat de resultaten van de ingevulde sheet capaciteitsplanningv2.xlsm zien. Het bovenste gedeelte is een snelle blik op de totale bezetting en per team. Door over de grafiek te hoveren met je muis kan je per week de laagste bezettingen per werknemer zien.
                  Het tweede gedeelte is bedoeld om specifiek per werknemer te bekijken hoe de bezetting verloopt over het jaar en hoe de verdeling van projecten van de werknemer in elkaar zit. Al deze data is gebaseerd op wat de werknemer zelf ingevuld heeft in de capaciteitsplanning.''')
        ]),
    ],
    style={
    'borderBottom': 'thin lightgrey solid',
    'backgroundColor': 'rgb(250, 250, 250)',
    'padding': '10px 5px'}
    ),
     
    #Set row with timeseries of total bezetting at the top
    html.Div([
        dcc.Graph(
            id='timeseries-total',
            hoverData={'points': [{'x': weekNumber}]})],

        #Define style of this html block
        style={'width': 1000, 'display': 'inline-block', 'padding': 10}),
    
    html.Div([
        dcc.Graph(id='barchart-wn')],
        style={'width': 600, 'display': 'inline-block', 'padding': 10}),
    
    #Dropdown for Vakgroep
    html.Div([
        
        html.Label(
            html.B('Teams')),
        
        dcc.Checklist(
            id ='checkboxes-vakgroepen',
            options=[{'label': i, 'value': i} for i in vg_indicator],
            value=['GW', 'OW', 'WG'],
            labelStyle = {'display': 'inline-block'})
        ],
        #Define style of this html block
        style={'width': 200, 'float': 'middle', 'display': 'block', 'padding': 20}),
    
    html.Hr(),
    
    #Dropdown for Werknemer
    html.Div([
        html.Label(
            html.B('Werknemer')),
        dcc.Dropdown(
            id='crossfilter-yaxis-column1',
            options=[{'label': i, 'value': i} for i in wn_indicator],
            value='Christian Bouman'),
        ], 
        #Define style of this html block
        style={'width': 300, 'float': 'upperleft', 'display': 'block', 'padding': 20}),
    
    #Graph for Werknemer    
    html.Div([
        dcc.Graph(
            id='crossfilter-timeseries')
            ], style={'width': 400, 'display': 'inline-block', 'padding': 20}),
    
    #Pie chart for Werknemer
    html.Div([
        dcc.Graph(
            id='piechart-crossfilter-projects')
        ], style={'width': 400, 'display': 'inline-block', 'padding': 20})
])
        
#%% Define callback options based on werknemer changes
@app.callback(
    dash.dependencies.Output('crossfilter-timeseries', 'figure'),
    [dash.dependencies.Input('crossfilter-yaxis-column1', 'value')])

# Create timeseries
def update_graph(yaxis_column_name):
    dff = df_wn_per
    return {
        'data': [dict(
            x=dff[dff['Werknemer'] == yaxis_column_name]['Week'],
            y=dff[dff['Werknemer'] == yaxis_column_name]['Bezetting'],
            mode='lines+markers',
            opacity=0.5,
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            title='Bezetting voor '+str(yaxis_column_name),
            xaxis= {
                'title': 'Weeknummer',
                'type': 'linear',
                'tick0': 0,
                'dtick': 5},
            yaxis= {
                'title': 'Bezetting (%)',
                'dtick': 10},
            margin={'l': 40, 'b': 50, 't': 40, 'r': 10},
            hovermode='x',
            height=400,
        )
    }

#%% Callback option based on vakgroep changes
@app.callback(
    dash.dependencies.Output('timeseries-total', 'figure'),
    [dash.dependencies.Input('checkboxes-vakgroepen', 'value')])

# Create timeseries
def update_graph2(yaxis_column_name2):
    dff1 = df_vg_per
    traces = [dict(
        x=df_tot['Week'],
        y=df_tot['Bezetting'],                           
        name='Totaal',
        mode='lines+markers',
        opacity=0.5,
        marker={
            'size': 10,
            'opacity': 0.5,
            'line': {'width': 0.5, 'color': 'white'}})]
    if yaxis_column_name2:
        for i in yaxis_column_name2:
            df_by_vakgroep = dff1[dff1['Vakgroep'] == i]
            traces.append(
                dict(
                    x=df_by_vakgroep['Week'],
                    y=df_by_vakgroep['Bezetting'],
                    mode='lines+markers',
                    opacity=0.5,
                    marker={
                        'size': 10,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}},
                    name=i))
    
    return{
        'data': traces,
        'layout': dict(
            title = 'Bezetting totaal en per team',
            xaxis= {
                'title': 'Weeknummer',
                'type': 'linear',
                'tick0': 0,
                'dtick': 2},
            yaxis= {
                'title': 'Bezetting (%)',
                'dtick': 10},
            margin= {'l': 50, 'r': 20, 'b': 50, 't': 50},
            hovermode= 'x',
            height= 400)
        }

#%% Callback option based on hover over vakgroep timeseries
@app.callback(
    dash.dependencies.Output('barchart-wn', 'figure'),
    [dash.dependencies.Input('timeseries-total', 'hoverData')])

# Create horizontal bar chart for werknemers in week
def update_wn_list(hoverData):
        week = hoverData['points'][0]['x']
        dff = df_wn_per[df_wn_per['Week'] == str(week)]
        dff = dff[dff['Bezetting'] < 30].sort_values(by='Bezetting', ascending=False)
        barchart = [go.Bar(
            x = dff['Bezetting'],
            y = dff['Werknemer'],
            orientation = 'h',
        opacity= 0.5)]
        return{
            'data': barchart,
            'layout': dict(
                title='Bezetting onder 30% week '+str(week),
                xaxis= {
                    'title': 'Bezetting (%)',
                    'dtick': 5},
                height= 400,
                orientation= 'h',
                margin= {'l': 200, 'r': 50, 'b': 50, 't': 50},
                )
            }
        
#%% Callback option based on Werknemer changes
@app.callback(
    dash.dependencies.Output('piechart-crossfilter-projects', 'figure'),
    [dash.dependencies.Input('crossfilter-yaxis-column1', 'value')])

# Create piechart based on werknemer selection
def update_piechart(werknemer):
    dff = df_proj_abs
    dff_wn = dff[dff['Werknemer'] == werknemer]
    piechart = [go.Pie(
            labels= dff_wn['Projectnaam'],
            values = dff_wn['Uren'],
            hole=.3,)]
    return {
        'data': piechart,
        'layout': dict(
            title='Projecten van '+str(werknemer),
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            height=400,
            showlegend=False)
        }
#%% Run app on server
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)       
