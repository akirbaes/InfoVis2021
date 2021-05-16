import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
import os
import time
from shapely.geometry import Point, Polygon

start_time = time.time()
last_time = time.time()

def timer():
    global start_time
    old_time = start_time
    start_time=time.time()
    return start_time-old_time
def timerstring():
    s=str(timer())
    if("." in s):
        s=s[:s.index(".")+2]
    return s.ljust(5)+"s "

def laptime():
    global last_time
    old_time = last_time
    last_time=time.time()
    return last_time-old_time
def lapstring():
    s=str(laptime())
    if("." in s):
        s=s[:s.index(".")+2]
    return s.ljust(5)+"s "
	
laptime()


external_stylesheets = ["https://codepen.iochriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
colors = {
    'background': '#F8F8F8',
    'text': '#011020'
}
#load_data
def load_all_data():
    path="SIMPLIFIED_DATA"
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith(("BIRCHES.shp")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                print("Open",str(counter),pathname)
                counter+=1
                db = gpd.read_file(pathname)
                print(timerstring(),"Finished reading database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db)
                
                #print(timerstring(),"Merged databases")
                print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata
#data is in alldata

alldata = load_all_data()



categories=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
cat_colors=[(212,212,212),(100,100,100),(70,3,89),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
cat_names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
class_names = list()
for dirpath, dirnames, filenames in os.walk("SIMPLIFIED_DATA"):
    for name in filenames:
        if name.endswith((".shp")):
            class_names.append(name[:-4])
print(len(class_names),class_names)
image_filenames = dict()
images_path = "RASTERISED_DATA/alpha300dpi_cropped/"
for dirpath, dirnames, filenames in os.walk(images_path):
    for name in filenames:
        for cat in categories:
            if ")"+cat+"_" in name:
                for classe in class_names:
                    if classe in name:
                        image_filenames[(cat,classe)]=images_path+name

"""fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)"""

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns[:-2]])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns[:-2] 
                ])for i in range(min(len(dataframe),max_rows))
            ])
        ])

print(alldata.head(10))
print(alldata.columns)

print("My crs:",alldata.crs)

point_coords = [60,60]



def recalculate_intersection(point_coords,selected_categories):
    #global intersection
    point = gpd.GeoSeries(Point(point_coords))
    point=gpd.GeoDataFrame(geometry=point)
    point.set_crs(epsg=4326,inplace=True)
    print("Point's crs:",point.crs)
    print(selected_categories)
    relevant_data = alldata.loc[alldata["category"].isin(selected_categories)]
    intersection = gpd.sjoin(relevant_data, point, op='intersects')
    print("Intersection:",len(intersection))
    print(intersection.head(20))
    return intersection
    
import plotly.graph_objects as go

import pprint

def update_map(geodata):
    palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
    def get_color(cat):
        return palette.index(cat)
    geodata["number"]=geodata.index
    geodata["color"]=geodata["category"].apply(get_color)
    max_color=geodata["color"].max()
    values = [i for i in range(max_color)]
    ticks = [i for i in range(max_color)]
    geodata=geodata.filter(["color","geometry","number"])
    print("####Received geodata:")
    print(geodata.head())
    gj = geodata.to_json()
    print("Received geojson:")
    pprint.pprint(gj)
    #print(geojson.dumps(parsed, indent=4))
    fig = px.choropleth_mapbox(geodata,
        geojson=gj,
        locations="number",
        color=geodata["color"],
        range_color=(0,geodata["color"].max()),
        mapbox_style="white-bg"
        )
    fig.update_geos(
        projection={"type": "cassini"}
        )
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0},
    coloraxis_colorbar={
        'title':'Extinction rate',
        'tickvals':values,
        'ticktext':ticks        
        }
    )   
    
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    
    coordinates = [[-180, 89],
               [180, 89],
               [180, -89],
               [-180, -89]]
    from PIL import Image
    img = Image.open('RASTERISED_DATA/alpha300dpi_cropped/MAMMALS.shp_(3)VU_300DPI.png')
    img = Image.open('allmammals.png')
    img = Image.open('RASTERISED_DATA/red100/alpha100DPIMARINEFISH_PART1.shp_(1)LC.png')
    fig.update_layout(
        mapbox_layers = [
        {
            "sourcetype": "image",
            "source": img,
            "coordinates":coordinates
            }]
            )
    fig.show()
    return fig

plotlyConfig = {'topojsonURL':'http://127.0.0.1:%i/assets/'%5500} 

multiselect_options = [{"label":classe,"value":classe} for classe in class_names]
multiselect_values = class_names[:]

#checklist_options  = [{"label":html.Mark(children=cat_names[i],id=cat),"value":cat} for i,cat in enumerate(categories)]
checklist_options  = [{"label":cat_names[i],"value":cat} for i,cat in enumerate(categories)]
checklist_values = categories[:]

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
    html.H1(children="Worldwide Animal Extinction Status",
        style={"textAlign":"center","color":colors["text"]}
        ),
    html.Div(
    children="Animal extinction status across the world. Click on the map"),
    
    html.Div(children=[
        html.Label(id="animals_count"),
        " animals at ",
        dcc.Input(id='longitude', value=str(point_coords[0]), type='number'),
        dcc.Input(id='latitude', value=str(point_coords[1]), type='number')
    ]),
    dcc.Graph(id="map_graph",config=plotlyConfig), 
    
    html.Button("Select all",id="select_all_classes"),
    html.Label(' or Select the databases to search in'),
    dcc.Dropdown(
        id="selected_classes",
        options=multiselect_options,
        value=multiselect_values,
        multi=True
    ),
    html.Label('Select the extinction level categories to search in'),
    dcc.Checklist(
        options=checklist_options,
        value=checklist_values,
        id="extinction_category"
    ),
    html.Div(children="Table area",id="table_to_fill")
])

from dash.dependencies import Input, Output


@app.callback(
    Output(component_id='table_to_fill', component_property='children'),
    Output(component_id='animals_count', component_property="children"),
    Output(component_id="map_graph", component_property="figure"),
    Input(component_id='longitude', component_property='value'),
    Input(component_id='latitude', component_property='value'),
    Input(component_id='extinction_category', component_property='value')
)
def update_animals_list(longitude, latitude, selected_categories):
    point_coords=[float(longitude),float(latitude)]
    intersection=recalculate_intersection(point_coords, selected_categories)
    fig = update_map(alldata)
    
    return generate_table(intersection,10), len(intersection), fig

@app.callback(
    Output(component_id='selected_classes', component_property='value'),
    Input(component_id='select_all_classes', component_property='n_clicks')
)
def set_all_classes(ignore):
    return class_names[:]



if __name__ == "__main__":
    app.run_server(debug=True)