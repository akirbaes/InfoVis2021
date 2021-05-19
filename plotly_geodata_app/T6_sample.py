# python D:\DAMA_Notes\Semester2\IV\project\myCodes\T6_sample.py

import pandas as pd
import matplotlib.pyplot as plt
import pycountry  # generate country code  based on country name 
# import pysal
import os
import numpy as np
import plotly.graph_objects as go
import geopandas
import plotly.express as px
import plotly.io as pio
from copy import deepcopy
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os

app = dash.Dash(__name__)


# Visualizaing Table 6
# Tab2=pd.read_csv(os.path.relpath('InfoVis2021/Table6_processed/redlist/processedTable/table2_processed_main.csv'))
Tab2=pd.read_csv(('table2_processed_main.csv'))
Tab2_CR=Tab2[Tab2['Threatened_category']=='CR']
Tab2_EN=Tab2[Tab2['Threatened_category']=='EN']
Tab2_VU=Tab2[Tab2['Threatened_category']=='VU']

years = ["1996", "1998", "2000", "2002", "2003", "2004", "2006", "2007", "2008", "2009","2010"
        ,"2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
         
def barchart_tab2(bar_categ,threat_limit):
    Tab2_bar=px.bar(
        data_frame=bar_categ,
        x="Classification_organism",
        y="Number_of_Species",
        color="Classification_organism",
        opacity=0.9,
        orientation="v",
        barmode="relative",
        labels={"Classification_organism":"organisms",
                "Number_of_Species":"Number of Threatened"},
        title='Changes in numbers of species in the threatened categories (CR, EN, VU) from 1996 to 2020',
        #  for the major taxonomic groups on the Red List"
        width=1250,
        height=550,
        color_discrete_map={"Mammals": "#990000" ,"Birds":"#4a1486","Amphibians":"#fc9272",
                            "Fishes":"#034e7b","Insects":"#737373","Molluscs":"#8c2d04",
                            "Other invertebrates":"#fcbba1","Plants":"#005824",
                            "Fungi&protists":"#f16913","Total":"#d9f0a3"},
        template='gridon',
        animation_frame='Year',
        range_y= threat_limit,
        category_orders={'Year':
            ["2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011","2010"
                ,"2009", "2008", "2007", "2006", "2004", "2003", "2002", "2000", "1998", "1996"]}
    )
    return Tab2_bar

CR_bar= barchart_tab2(Tab2_CR,[0,8000])
EN_bar= barchart_tab2(Tab2_EN,[0,14000])
VU_bar= barchart_tab2(Tab2_VU,[0,15000])

bar_tab2_animations={
    'Critically Endangered (CR)':CR_bar,
    'Endangered (EN)':EN_bar,
    'Vulnerable (VU)':VU_bar
}

# Visualizaing Table 6
Tab6=pd.read_csv('Tab6_CountryCode.csv')

Tab6_animal = Tab6.query('species=="animal"', inplace = False)
Tab6_plant = Tab6.query('species=="plant"', inplace = False)
Tab6_chromist = Tab6.query('species=="chromist"', inplace = False)
Tab6_fungi = Tab6.query('species=="fungus"', inplace = False)

def createGraph(table,heading,colorbarTitle,colorScale,visible):
    data=go.Choropleth(
        locations = table['CODE'],
        z = table['Total'].replace(',','', regex=True).astype(int),
        # zmax=10000,
        # zmin=1000,
        # zmid=5000,
        zauto=True,
        meta= table['Name']+";"+ table['EX'].astype(str)
                        +";"+ table['EW'].astype(str)
                        +";"+ table['CR(PE)'].astype(str)
                        +";"+ table['CR(PEW)'].astype(str)
                        +";"+ table['CR'].astype(str)
                        +";"+ table['EN'].astype(str)
                        +";"+ table['VU'].astype(str)
                        +";"+ table['LR/cd'].astype(str)
                        +";"+ table['NT or LR/nt'].astype(str)
                        +";"+ table['LC or LR/lc'].astype(str)
                        +";"+ table['DD'].astype(str),
        
        
        
        text = table['Name'],
        colorscale = colorScale,
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title = heading,
        visible = visible,
    )

    return data
    # data.write_html("D:\DAMA_Notes\Semester2\IV\project\myCodes\\animalPlotted.html")


animalColorScale=[[0, 'rgb(254,229,217)'], 
                    [0.25, 'rgb(252,174,145)'],
                    [0.5, 'rgb(251,106,74)'],
                    [1.0, 'rgb(203,24,29)']
                ]
animalFig=createGraph(Tab6_animal,"Threatened Animals","Threatened Animals",animalColorScale,True)

plantColorScale=[[0, 'rgb(237,248,233)'], 
                    [0.25, 'rgb(186,228,179)'],
                    [0.5, 'rgb(116,196,118)'],
                    [1.0, 'rgb(35,139,69)']
                ]
plantFig=createGraph(Tab6_plant,"Threatened Plants","Threatened Plants",plantColorScale,False)

fungiColorScale=[[0, 'rgb(254,237,222)'], 
                    [0.25, 'rgb(253,190,133)'],
                    [0.5, 'rgb(253,141,60)'],
                    [1.0, 'rgb(217,71,1)']
                ]    
fungiFig = createGraph(Tab6_fungi,"Threatened Fungi","Threatened Fungi",fungiColorScale,False)

chromistColorScale=[[0, 'rgb(239,243,255)'], 
                    [0.25, 'rgb(189,215,231)'],
                    [0.5, 'rgb(107,174,214)'],
                    [1.0, 'rgb(33,113,181)']
                ]    
chromistFig = createGraph(Tab6_chromist,"Threatened Chromist","Threatened Chromist",chromistColorScale,False)

graphToShow=[animalFig,plantFig,fungiFig,chromistFig]
labels = ["Animal","Plant","Fungi","Chromist"]
# is going to be visible
visible = np.array(labels)

traces = []
buttons = []
for value in labels:
    buttons.append(dict(label=value,
                        method='update',
                        args=[{"visible":list(visible==value)},
                              {"title":f"<b>{value}</b>"}
                        ]
                    ),
                )
updatemenus = [{"active":0,
                "buttons":buttons,
                "direction": 'up',
                }]       
# Show figure
speciesFig = go.Figure(data=graphToShow,
                layout=dict(updatemenus=updatemenus))
                # speciesFig = go.Figure(data=traces,
                # layout=dict(updatemenus=updatemenus))
# This is in order to get the first title displayed correctly
first_title = labels[0]
speciesFig.update_layout(title=f"<b>{first_title}</b>",title_x=0.5)

from plotly_visualisation_cursor import *

# http://127.0.0.1:8050/
# https://www.phillipsj.net/posts/creating-maps-with-dash/
app.layout = html.Div(children=[
    html.H1(
        className="app-header",
        children=[
            html.Div('Red List', className="app-header--title")
        ]),    
    html.Div(
        id="custom",
        className="custom",
        children=[
        html.Div( style={'margin-top': '190px','height':'20px','border-top':'solid 2px black','font-weight':'bold'},
               id="details1",className="sidebar"),
        html.Div(style={'margin-top': '213px','height':'20px'},
                id="details2",className="sidebar"),
        html.Div(style={'margin-top': '234px','height':'20px'},
                id="details3",className="sidebar"),
        html.Div(style={'margin-top': '255px','height':'49px'},
                id="details4",className="sidebar"),
        html.Div(style={'margin-top': '305px','height':'49px'},
                id="details5",className="sidebar"),
        html.Div(style={'margin-top': '355px','height':'17px'},
                id="details6",className="sidebar"),
        html.Div(style={'margin-top': '373px','height':'19px'},
                id="details7",className="sidebar"),
        html.Div(style={'margin-top': '394px', 'height':'20px'},
                id="details8",className="sidebar"),
        html.Div(style={'margin-top': '415px','height':'31px'},
                id="details9",className="sidebar"),
        html.Div(style={'margin-top': '447px','height':'46px'},
                id="details10",className="sidebar"),
        html.Div(style={'margin-top': '494px','height':'46px'},
                id="details11",className="sidebar"),
        html.Div(style={'margin-top': '541px','height':'20px','border-bottom':'solid 2px black'},
                id="details12",className="sidebar"),                      
    ]),
    dcc.Graph(
        className="custom",
        id='example-map',
        figure=speciesFig
    ),
    html.Div([
        html.P("Select the threatened category:"),
        dcc.RadioItems(
            id='selection',
            options=[{'label': x, 'value': x} for x in bar_tab2_animations],
            value='Critically Endangered (CR)'
        ),
        dcc.Graph(id="graph"),
    ])
    ,
    layout
])
  

# call back for Table 2 visulaization
@app.callback(

     Output('graph', 'figure'),
    [Input('selection', 'value')]

)
 
def update_figure(value):   
    name = ""
    meta = ""
    metaData =["","","","","","","","","","","",""]  
    print(value)

    return(bar_tab2_animations[value])


# call back for Table 6 visulaization
@app.callback(
    [Output('details1', 'children'),
    Output('details2', 'children'),
    Output('details3', 'children'),
    Output('details4', 'children'),
    Output('details5', 'children'),
    Output('details6', 'children'),
    Output('details7', 'children'),
    Output('details8', 'children'),
    Output('details9', 'children'),
    Output('details10', 'children'),
    Output('details11', 'children'),
    Output('details12', 'children')],
    [Input('example-map', 'clickData')]

)
 
def update_meta(clickData):   
    name = ""
    meta = ""
    metaData =["","","","","","","","","","","",""]
    if clickData is not None:            
        name = clickData['points'][0]['text']
        meta = clickData['points'][0]['meta']
        print(name)
        metaData=meta.split(";")
    


    return ([metaData[0],
    "Extinct: {}".format(metaData[1]),
    "Extinct in the Wild: {}".format(metaData[2]),
    "Critically Endangered(Possibly Extinct) :{}".format(metaData[3]),
    "Critically Endangered(Possibly Extinct & Reintroduced): {}".format(metaData[4]),
    "Critically Endangered: {}".format(metaData[5]),
    "Endangered: {}".format(metaData[6]),
    "Vulnerable: {}".format(metaData[7]),
    "Lower Risk/conservation dependent: {}".format(metaData[8]),
    "Near Threatened (includes LR/nt - Lower Risk/near threatened): {}".format(metaData[9]),
    "Least Concern (includes LR/lc - Lower Risk, least concern): {}".format(metaData[10]),
    "Data Deficient: {}".format(metaData[11])])


if __name__ == '__main__':
    app.run_server(debug=True)
