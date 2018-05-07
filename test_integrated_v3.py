import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from googlemaps_api import *
from NearestElement import *

app = dash.Dash()
server = app.server


mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'


def initialize():
    df = pd.read_csv('hydrant_loc.csv')
    df.drop("Unnamed: 0", 1, inplace=True)
    df.drop("OutOfService", 1, inplace=True)
    df.drop("Critical", 1, inplace=True)
    df.drop("CriticalNotes", 1, inplace=True)
    return df


app.layout = html.Div([
    html.H1(
        children='Find nearest fire hydrant',
        style={
            'textAlign': 'center',
            'fontSize':'30px'
        }
    ),

    html.Div([
        html.Div([

            html.Label('Please input your address'),
            dcc.Input(id = 'cur_loc', value='200 N White Horse Pike, Lawnside, NJ 08045, USA', type='text',className = 'eigth columns'),

            html.Label('Please select number of nearest hydrant'),
            dcc.RadioItems(
                id = 'top',
                options=[
                    {'label': 'Top 1', 'value': 1},
                    {'label': 'Top 3', 'value': 3},
                    {'label': 'Top 5', 'value': 5}
                ],
                value=1,
                labelStyle={'display': 'inline-block'},
                className = 'eigth columns'),

            html.Label('Please select distance type'),

            dcc.RadioItems(
                id = 'distance',
                options=[
                    {'label': 'Haversine distance', 'value': 'hev'},
                    {'label': 'walk distance', 'value': 'walking'},
                    {'label': 'drive distance', 'value': 'driving'}
                ],
                value='hev',
                labelStyle={'display': 'inline-block'},
                className = 'eigth columns'),




            html.Div([html.Label('Drag to control searching range'),
            dcc.Slider(
                id="my-slider",
                max = 20,
                min=1,
                step=1,
                value=1,
                marks = {i: 'km {}'.format(i) if i == 1 else str(i) for i in range(1, 21)},
                className = 'eigth columns',
            )], style={'marginBottom': 60,'textAlign':'center'}),


            html.Button(id='submit-button', n_clicks=0, children='Submit',className= 'eigth columns'),

            #html.Iframe(id = 'message',srcDoc='test',className = 'eigth columns',style=dict(marginTop= '40'))
            html.Div(children='''
                Status of Hydrants
                ''',id ='message',
                #className = 'eight columns',
                     className = 'row',
                style = dict(className = 'eigth columns',fontSize='15px', textAlign='center')),
            html.Iframe(id = 'iframe-msg',srcDoc='message',width = 450,style=dict(className= 'eigth columns',textAlign='center'))
            #html.H1(children='Hello Dash')
            # html.Div([children = INFO,
            #     id ='chem_desc',
            #     style = dict( maxHeight='500px',maxWidth="350px", fontSize='13px' )),
            # ],className ='eigth columns',style=dict(height='500px',textAlign='center')

            ],className ='six columns',style=dict(height='300px',textAlign='center')),

    html.Div([
        dcc.Graph(id='map-graph'),
        ], className='six columns',style={'textAlign':'center'})


    ],style={"padding-top": "20px",'textAlign':'center'})
],style = {'textAlign':'center'})


@app.callback(Output("iframe-msg", "srcDoc"),
              [Input('submit-button', 'n_clicks')],
              [State('cur_loc', 'value'),
               State('my-slider', 'value'),
               State('top', 'value'),
               State('distance', 'value'),
               ])
def update_message(click,curloc, my_slider, topnum, distance_type):
    ## call backend function and return description of the nearest hydrant
    [latInitial, lonInitial] = get_Geocode(curloc)
#    global output_pd
    output_pd = hydrants.get_nearest_fast_allinOne(lonInitial, latInitial, my_slider, topnum, 'km', distance_type)
#    output_str = ''
#    if len(output_pd) == 0:
#        output_str = 'No working hydrant found nearby, please consider increase the search diameter'
#    else:
#        for i in range(len(output_pd)):
#            header = '*  Rank '  + str(i) + ' closest working hydrant:\n'
#            address = '  - Address: ' + get_address([output_pd.iloc[i]['Lat'], output_pd.iloc[i]['Lon']]) + '\n'
#            if output_pd.iloc[i]['CriticalNotes'] is None:
#                criticalNotes = '  - Critical Notes: None. \n'
#            else:
#                criticalNotes = '  - Critical Notes: ' + output_pd.iloc[i]['CriticalNotes'] + '\n' + '\n'
#            output_str += (header + address + criticalNotes)
    return output_pd.to_html()




@app.callback(Output("map-graph", "figure"),
              [Input('submit-button','n_clicks')],
              [State('cur_loc', 'value'),
               State('my-slider', 'value'),
               State('top', 'value'),
               State('distance','value'),
               State('map-graph', 'relayoutData'),
               ])
def update_graph(click,curloc, my_slider, topnum, distance_type,prevLayout):
    zoom = 13.0
#    latInitial = 39.9
#    lonInitial = -75.1
    bearing = 0
    mapControls = 'lock'
    
    
    [latInitial, lonInitial] = get_Geocode(curloc)
    output_pd = hydrants.get_nearest_fast_allinOne(lonInitial, latInitial, my_slider, topnum, 'km', distance_type)
    output_pd.drop("OutOfService", 1, inplace=True)
    output_pd.drop("Critical", 1, inplace=True)
    output_pd.drop("CriticalNotes", 1, inplace=True)
    
    listStr = 'output_pd'

    datas = []
    data0 = Data([
        Scattermapbox(
            lat=[latInitial],
            lon=[lonInitial],
            mode='markers',
            hoverinfo="lat+lon",
            #                 text=eval(listStr).index.hour,
            marker=Marker(
                size=14,
                color = 'red'
            ),
        ),
    ])
    datas.extend(data0)
    data1 = Data([
        Scattermapbox(
            lat=eval(listStr)['Lat'],
            lon=eval(listStr)['Lon'],
            mode='markers',
            hoverinfo="lat+lon",
            #                 text=eval(listStr).index.hour,
            marker=Marker(
                size=14,
                color = 'blue'
            ),
        ),
    ])
    datas.extend(data1)
    layout=Layout(
            autosize=True,
            height=500,
            #width=800,
            margin=Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial, # 40.7272
                    lon=lonInitial # -73.991251
                ),
                style='dark',
                bearing=bearing,
                zoom=zoom
            ),
            updatemenus=[
                dict(
                    buttons=([
                        dict(
                            args=[{
                                    'mapbox.zoom': 12,
                                    'mapbox.center.lon': '-75.1',
                                    'mapbox.center.lat': '39.9',
                                    'mapbox.bearing': 0,
                                    'mapbox.style': 'dark'
                                }],
                            label='Reset Zoom',
                            method='relayout'
                        )
                    ]),
                    direction='left',
                    pad={'r': 0, 't': 0, 'b': 0, 'l': 0},
                    showactive=False,
                    type='buttons',
                    x=0.45,
                    xanchor='left',
                    yanchor='bottom',
                    bgcolor='#323130',
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(
                        color="#FFFFFF"
                    ),
                    y=0.02
                ),
            ]
        )
    return go.Figure(data=datas, layout=layout)






external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]


for css in external_css:
    app.css.append_css({"external_url": css})


@app.server.before_first_request
def defineTotalList():
    global totalList
    totalList = initialize()
    global hydrants
    hydrants = data_generator('/Users/Joe/Desktop/phillyCODEFEST/hydrants.json')


if __name__ == '__main__':
    app.run_server(debug=True)
