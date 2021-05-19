import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
import os
import time
from shapely.geometry import Point, Polygon
import plotly.graph_objects as go
import pprint
import pyproj

start_time = time.time()
last_time = time.time()
selected_shapes = None #Should not be a global if we want the server to serve several pages

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
def timestamp():
    return datetime.now().strftime("%H:%M:%S")
	

external_stylesheets = ["https://codepen.iochriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
colors = {
    'background': '#F8F8F8',
    'text': '#011020'
}

def count_all_extension(path,extension):
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith(extension):
                counter+=1
    return counter
    

def load_all_data(path):
    has_data = False
    alldata = None
    counter = 0
    ext = ".shp"
    total_counter = count_all_extension(path,ext)
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            # print("#"*20+name)
            if name.endswith(ext) and counter<8: #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                print("Open %i/%i"%(counter,total_counter),pathname)
                counter+=1
                db = gpd.read_file(pathname)
                db["origin"]=name
                # print(timerstring(),"Finished reading database")
                
                def get_area(entry):
                    return entry.area
                db=db.explode()
                db["area"]=db["geometry"].apply(get_area)
                db=db[db["area"]>0.05]
                db=db.reset_index(drop=True)
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db,ignore_index=False)
                print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata

#aggregated_data = gpd.read_file("AGGREGATED_DATA/_agg_LOBSTERS.shp")
path="assets/Mammals_server/AGGREGATED_DATA"
path="assets/Heavy_server/AGGREGATED_DATA"
path="assets/Light_server/AGGREGATED_DATA"
aggregated_data = load_all_data(path)
def get_file_name(origin):
    return origin[5:-4]
aggregated_data["origin"]=aggregated_data["origin"].apply(get_file_name)
available_databases = list(aggregated_data["origin"].unique())
print("Finished loading all available aggregated data")
print(aggregated_data)

#aggregated_data = gpd.read_file("AGGREGATED_DATA/_agg_LOBSTERS.shp")
path="assets/Mammals_server/SIMPLIFIED_DATA"
path="assets/Heavy_server/SIMPLIFIED_DATA"
path="assets/Light_server/SIMPLIFIED_DATA"
alldata = load_all_data(path)
def get_file_name(origin):
    return origin[:-4]
alldata["origin"]=alldata["origin"].apply(get_file_name)
print("Finished loading all simplified habitat data")
print(alldata)



categories=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
palette=categories
cat_names = ["Data defficient","Least concern", "Lower risk", "Near threatened", "Conservation dependent-", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
cat_colors=[(212,212,212),(100,100,100),(90,70,100),(70,3,89),(60,30,100),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
cat_colors=list("#"+"".join((("{:02x}".format(c) for c in col))) for col in cat_colors)

color_of_catid = {id:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_category = {cat:cat_colors[id] for (id,cat) in enumerate(cat_names)}

import dash_table
def generate_table(dataframe, max_rows=10):
    selection = ["binomial","kingdom","phylum","class","order_","family","genus","category"]
    limit = dataframe.columns
    selection = [x for x in selection if x in limit]
    dataframe=dataframe.filter(selection).drop_duplicates(ignore_index=True)
    
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col.center(24)) for col in selection])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col].center(24)) for col in selection 
                ])for i in range(min(len(dataframe),max_rows))
            ])
        ])
    # return dash_table.DataTable(
    # data=dataframe,
    # columns=[{'id': c, 'name': c} for c in dataframe.columns],
    # page_action='none',
    # style_table={'height': '300px', 'overflowY': 'auto'}
    # )


# print("My crs:",alldata.crs)

# def subset_by(database, column=None, identifier=None, terrains=None, categories=None):
    # return subset(database, (column, identifier, terrains, categories))

# def subset(database, selector):
    # column, identifier, terrains, categories = selector
    # if(column!="global" and column!=None):
        # database = database[database[column]==identifier]
    # if(terrains!=None):
        # all_terrains = ("marine","terrestial","freshwater")
        # truth = [t in terrains and "true" or "irrelevant" for t in all_terrains]
        # marine,terrestial,freshwater = truth
        # database = database[(database["marine"]==marine) | (database["terrestial"]==terrestial) | (database["freshwater"]==freshwater)]
    # if(categories!=None):
        # database = database.loc[database["category"].isin(categories)]
    # return database

def recalculate_intersection(point_coords, selected_database_name):
    #global intersection
    point = gpd.GeoSeries(Point(point_coords))
    point=gpd.GeoDataFrame(geometry=point)
    point.set_crs(epsg=4326,inplace=True)
    # print("Point's crs:",point.crs)
    # print(selected_categories)
    # relevant_data = alldata.loc[alldata["category"].isin(selected_categories)]
    intersection = gpd.sjoin(alldata[alldata["origin"]==selected_database_name].explode().reset_index(), point, op='intersects')
    print("Intersection:",len(intersection))
    print(intersection.head(20))
    print("Calculations done")
    return intersection
    
    


def update_map_agg(geodata,levels):
    def get_color(cat):
        return palette.index(cat)
    geodata["color"]=geodata["category"].apply(get_color)
    geodata.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    geodata = geodata[geodata['category'].isin(levels)]
    geodata["index"]=geodata.index
    #geodata["identifier"]="Lobster"
    #geodata["id_type"]="order_"
    # columns = ["binomial","kingdom","phylum","class","order_","family","genus","category"]
    
    columns = ["identifier","id_type","category"]
    columns = ["category"]
    def get_full_name(color):
        return cat_names[color]
    geodata["category"]=geodata["color"].apply(get_full_name)
    # def get_file_name(origin):
        # return origin[5:-4]
    # geodata["origin"]=geodata["origin"].apply(get_file_name)
    # geodata=geodata.explode().reset_index()
    show = {c:True for c in columns}
    show["color"]=False
    show["index"]=False
    if(len(geodata)==0):
        geodata.loc[0]=["" for c in geodata.columns]
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["origin"],
            opacity=1,
            width=1000, height=800,zoom=1)
    else:
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["origin"],
            opacity=0.8,
            width=1000, height=800,zoom=1)
    fig.update_layout(uirevision="don't update")
    fig.update_layout(clickmode='event+select')
    # fig.add_scattermapbox(lat=[0],lon=[0],opacity=0,mode = "lines+markers")
    # x,y=crosshair
    # # fig.add_shape(type="line",x0=x-1, y0=y, x1=x+1, y1=y)
    # # fig.add_shape(type="line",x0=x, y0=y-1, x1=x, y1=y+1)
    # fig.add_scattermapbox(lat = [x],lon = [y])
    return fig
    

def update_map_select(geodata,levels,crosshair):
    def get_color(cat):
        return palette.index(cat)
    
    # geodata=geodata.filter(["binomial","kingdom","phylum","class","order_","family","genus","category","geometry"])
    geodata["color"]=geodata["category"].apply(get_color)
    geodata.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    max_color=10
    values = [i for i in range(max_color)]
    ticks = [i for i in range(max_color)]
    # geodata=geodata.filter(["color","geometry","category"])
    geodata = geodata[geodata['category'].isin(levels)]
    # print("####Received geodata:",len(geodata))
    # print(geodata.head())
    geodata["index"]=geodata.index
    columns = ["category","origin","kingdom","phylum","class","order_","family","genus"]
    
    def get_full_name(color):
        return cat_names[color]
    geodata["category"]=geodata["color"].apply(get_full_name)
    show = {c:True for c in columns}
    show["color"]=False
    show["index"]=False
    #print(geojson.dumps(parsed, indent=4))
    if(len(geodata)==0):
        geodata.loc[0]=["" for c in geodata.columns]
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["binomial"],
            opacity=1,
            width=1000, height=800,zoom=1)
    else:
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["binomial"],
            opacity=0.7,
            width=1000, height=800,zoom=1)
    # fig.update_geos(fitbounds="locations")
    fig.update_layout(uirevision="don't update")
    fig.update_layout(clickmode='event+select')
    # fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    
    # coordinates = [[-180, 89],
               # [180, 89],
               # [180, -89],
               # [-180, -89]]
    # from PIL import Image
    # img = Image.open('RASTERISED_DATA/alpha300dpi_cropped/MAMMALS.shp_(3)VU_300DPI.png')
    # img = Image.open('allmammals.png')
    # img = Image.open('RASTERISED_DATA/red100/alpha100DPIMARINEFISH_PART1.shp_(1)LC.png')
    # fig.update_layout(
        # mapbox_layers = [
        # {
            # "sourcetype": "image",
            # "source": img,
            # "coordinates":coordinates
            # }]
            # )
    # fig.show()
    x,y=crosshair
    fig.add_scattermapbox(lat = [x],lon = [y], 
        mode='markers',
        marker=go.scattermapbox.Marker(size=14, color="red"),
        text=['Crosshair'],)
    # fig.add_scattermapbox(lat = [x],lon = [y])
    # fig.add_shape(type="line",x0=x-1, y0=y, x1=x+1, y1=y)
    # fig.add_shape(type="line",x0=x, y0=y-1, x1=x, y1=y+1)
    
    # trace = dict(
         # x=[crosshair[0]],
         # y=[crosshair[1]],
         # hoverinfo='skip'
        # )
    # fig.add_trace(trace)
    return fig

##################################################################################################################
##################################################################################################################
##################################################################################################################
#plotlyConfig = {'topojsonURL':'http://127.0.0.1:%i/assets/'%5500} 
#import T6_sample
# class_names = ['TETRAODONTIFORMES',"CHIMAERIFORMES"]
# multiselect_options = [{"label":classe,"value":classe} for classe in class_names]
# multiselect_values = class_names[:]

#checklist_options  = [{"label":html.Mark(children=cat_names[i],id=cat),"value":cat} for i,cat in enumerate(categories)]
checklist_options  = [{"label":cat_names[i],"value":cat} for i,cat in enumerate(categories)]
checklist_values = categories[:]

# habitat_values = ["Marine","Terestial","Freshwater"]
# habitat_options = [{"label":hab,"value":hab} for hab in habitat_values]

layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
    #T6_sample.app.layout,
    html.Hr(),
    html.H1(children="Worldwide Animal Extinction Status",
        style={"textAlign":"center","color":colors["text"]}
        ),
    html.Div(
    children="Animal extinction status across the world."),
    
    html.Label('Select the extinction level categories to search in'),
    dcc.Checklist(
        options=checklist_options,
        value=checklist_values,
        id="extinction_category"
    ),
    html.Button('Submit', id='submit_coords', n_clicks=0),
    html.Div(id="bigdiv",children=[
        dcc.Graph(id="map_graph"),#,config=plotlyConfig), 
        html.Label("+",id="crosshair"),
        html.Div(children=[
            html.Div(children=["Current database:",html.Label(id="selected_database_text")]),
            html.Div(children=[html.Button(dname, id=dname, n_clicks=0) for dname in available_databases]),
            html.Div(children=["Selection: ",html.Label("0 0",id="mouse_coord")," ",html.Button("Toggle selection",id="crosshair_selection")]),
            html.Hr(),
            html.Label("0",id="animals_count")," ",html.Label("animals",id="animal_type")," in ",html.Label("the world",id="selection_brag"),
            html.Hr(),
            html.Div(children="Table area",id="table_to_fill")]
            ,id="div_right"),
        dcc.Store(id="no_id")])
])

            # html.Label('Aggregation mode'),
            # dcc.Checklist(
                # options=[{"label":"Aggregate","value":"aggregate"}],
                # value=["aggregate"],
                # id="aggregate_toggle"
            # ),
##################################################################################################################
##################################################################################################################
##################################################################################################################

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

def search_aggregated_data(orders,modifs):
    files_list = set()
    path="ORDER_AGGREGATED_DATA"
    has_data = False
    ordata = None
    print(orders,modifs)
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS
                # print("Lookin at",name)
                for order in orders:
                    for modif in modifs:
                        if order in name and modif.lower() in name:
                            pathname =os.path.join(dirpath, name)
                            files_list.add(pathname)
    print("Files loaded to show:",files_list)
    for filename in files_list:
        db = gpd.read_file(pathname)
        if(has_data==False):
            ordata=db
            has_data=True
        else:
            ordata=ordata.append(db)
    ordata.reset_index(drop=True,inplace=True)
    return ordata
    
    
@app.callback(
    Output("selected_database_text","children"),
    Output("animal_type","children"),
    *(Input(dbname,"n_clicks") for dbname in available_databases)
    )
def set_selected_dbname(*nclicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        # button_id = 'No clicks yet'
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return button_id, button_id
    # if nckick == 0:
# @app.callback(
    # Output(component_id='table_to_fill', component_property='children'),
    # Output(component_id='animals_count', component_property="children"),
    # Output(component_id="map_graph", component_property="figure"),
    # Input(component_id='longitude', component_property='value'),
    # Input(component_id='latitude', component_property='value'),
    # Input(component_id='selected_classes', component_property='value'),
    # Input(component_id='extinction_category', component_property='value'),
    # Input(component_id='habitat_type', component_property='value'),
    # Input(component_id='aggregate', component_property='value')
# )
# def update_animals_list(longitude, latitude, selected_classes, selected_categories, selected_habitats, agg):
    # point_coords=[float(longitude),float(latitude)]
    # # if(agg):
    # # aggdata = search_aggregated_data(selected_classes,selected_habitats)
    # # print("Aggregated:",aggdata)
    # # fig = update_map_any(aggdata,selected_categories)
    # # intersection=[]
    # # else:
    # intersection=recalculate_intersection(point_coords,selected_categories)
    # #intersection = alldata
    # fig = update_map_any(intersection,selected_categories)
    # # print("App layout")
    # # print(app.layout)
    # # print(app.layout["map_graph"])
    # # print("Intersection found:",len(intersection))
    # return generate_table(intersection,10), len(intersection), fig
    # # return generate_table(alldata,10), len(alldata), fig
    
    # # Output('animals_count', 'children'),
    # # Output('table_to_fill', 'children'),
    # # Output('map_graph', 'figure'),
    
# @app.callback(
    # Output(
    # Output('intermediate_value', 'data'),
    # Input(selected_classes
    
    

# @app.callback(
    # Output('aggregate_toggle', 'value'),
    # Input('submit_coords', 'n_clicks')
    # )
# def start_looking_at_point(nclick):
    # print("Nclick:",nclick)
    # if nclick == 0:
        # raise PreventUpdate
    # return []

    #Output('intermediate_value', 'data'),
    # Input('longitude','value'),
    # Input('latitude','value'),
    
@app.callback(
    Output("mouse_coord","children"),
    Input("map_graph","relayoutData"))
def update_location(relayoutData):
    print("v"*20,relayoutData)
    # if(relayoutData and 'mapbox.center' in relayoutData):
        # x=relayoutData["mapbox.center"]["lon"]
        # y=relayoutData["mapbox.center"]["lat"]    
    if(relayoutData and 'mapbox._derived' in relayoutData):
        x,y=relayoutData["mapbox._derived"]["coordinates"][0]
        xx,yy=relayoutData["mapbox._derived"]["coordinates"][2]
        x=(float(x)+float(xx))/2
        y=(float(y)+float(yy))/2
        x,y=y,x
    # if(relayoutData and "xaxis.range[0]" in relayoutData):
        # x = relayoutData["xaxis.range[0]"]
        # xx = relayoutData["xaxis.range[1]"]
        # y = relayoutData["yaxis.range[0]"]
        # yy = relayoutData["yaxis.range[1]"]
        # coord = str((float(x)+float(xx))/2)+" "+str((float(y)+float(yy)))
        coord = "%.2f %.2f"%(float(x),float(y))
        return coord
    else:
        raise PreventUpdate
    
# def display_relayout_data(relayoutData):
    # return json.dumps(relayoutData, indent=2)
    #selectedData is useless now
@app.callback(
    Output('table_to_fill', 'children'),
    Output('animals_count', "children"),
    Output("selection_brag", "children"),
    Input("selected_database_text","children"),
    Input("crosshair_selection","n_clicks"),
    Input("mouse_coord","children")
)
def update_selection(selected_database_name,n_clicks,mouse_coords):
    x,y = (float(i) for i in mouse_coords.split())
    print(dash.callback_context.triggered)
    ctx = dash.callback_context
    # print("*"*20,relayoutData)
    # if(selectedData and "range" in selectedData):
        # #https://dash.plotly.com/interactive-graphing
        # x = sum(float(selectedData["range"]["x"]))/2
        # y = sum(float(selectedData["range"]["y"]))/2
        # point = (x,y)
    # if(relayoutData):
        # #https://dash.plotly.com/interactive-graphing
        # x = sum(float(selectedData["range"]["x"]))/2
        # y = sum(float(selectedData["range"]["y"]))/2
    if(n_clicks!=None and n_clicks%2):
        point = (x,y)
        print("Clicked at",point)
        sel=recalculate_intersection(point,selected_database_name)
        sel.reset_index(inplace=True,drop=True)
        global selected_shapes
        selected_shapes = sel
        # output_div = "Selection: [%4s:%4s] "%(x,y)
        return generate_table(selected_shapes,1000), len(selected_shapes), "%.2f %.2f"%(x,y)
        # and selectedData["range"]):
        # ranges = selectedpoints_local['range']
        # selection_bounds = {'x0': ranges['x'][0], 'x1': ranges['x'][1],
                            # 'y0': ranges['y'][0], 'y1': ranges['y'][1]}
        # point = (ranges['x'][0],ranges['y'][0])
    else:
        if(ctx.triggered!=None and "mouse_coord" in ctx.triggered[0]['prop_id'].split('.')[0]):
            raise PreventUpdate
        #raise PreventUpdate
        #point = (float(longitude),float(latitude))
        selected_animals = alldata[alldata["origin"]==selected_database_name]
        # output_text = "%4s %4s"%(x,y)
        return generate_table(selected_animals,1000), len(selected_animals), "the world"
    #sel = sel.to_json()
    # print("Received selection:")
    # print(sel)
    #return sel, 
    
    
# @app.callback(
    # Output("mouse_coord","data"),
    # dash.dependencies.Input("map_graph","hoverData"))
# def updage_pos(hoverData):
    # print(hoverData)
    # return "15 15"

import json
#from shapely import MultiPolygon
    #Input('intermediate_value', 'data'),
    # Input('longitude','value'),
    # Input('latitude','value'),
    #Input('aggregate_toggle','value'),
@app.callback(
    Output('map_graph', 'figure'),
    Input('extinction_category', 'value'),
    Input("selected_database_text","children"),
    Input("selection_brag","children"),
    Input("mouse_coord","children")
)
def update_graph_selection(classes,selected_database_name,selection_text,mouse_coords):
    ctx = dash.callback_context
    if(selection_text=="the world"):
        #if(ctx.triggered!=None and (ctx.triggered[0]['prop_id'].split('.')[0] not in ["selected_database_text","extinction_category"])):
        #    raise PreventUpdate
        graph=update_map_agg(aggregated_data[aggregated_data["origin"]==selected_database_name],classes)
    else:
        x,y = (float(i) for i in mouse_coords.split())
        gdf = selected_shapes
        graph = update_map_select(gdf,classes,(x,y))
    return graph

# @app.callback(
    # Output(component_id='selected_classes', component_property='value'),
    # Input(component_id='select_all_classes', component_property='n_clicks')
# )
# def set_all_classes(ignore):
    # return class_names[:]



if __name__ == "__main__":
    app.layout=layout
    app.run_server(debug=True)