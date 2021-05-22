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
from datetime import datetime

selected_shapes = [] #Should not be a global if we want the server to serve several pages
current_mode = "aggregate"
timer_values = {-1:time.time()}
def timer(index=0):
    global timer_values
    old_time = timer_values.get(index,timer_values[-1])
    timer_values[index]=time.time()
    return timer_values[index]-old_time
def timerstring(index=0):
    s=str(timer(index))
    if("." in s):
        s=s[:s.index(".")+2]
    return s.ljust(5)+"s "
def timestamp():
    return datetime.now().strftime("%H:%M:%S")
unchanged_graph = []
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
    


categories=['DD', 'LC', 'LR/lc', 'LR/cd', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
palette=categories
cat_names = ["Data defficient","Least concern", "Lower risk", "Conservation dependent", "Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
cat_colors=[(212,212,212),(100,100,100),(90,70,100),(70,3,89),(60,30,100),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
cat_colors=list("#"+"".join((("{:02x}".format(c) for c in col))) for col in cat_colors)

color_of_catid = {id:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_category = {cat:cat_colors[id] for (id,cat) in enumerate(cat_names)}


groupnames = ['BIRDS', 'MAMMALS', 'AMPHIBIANS', 'FISHES', 'CARTILAGINOUS FISHES', 'INSECTS', 'CRUSTACEANS', 'MOLLUSCS', 'PLANTS', 'FUNGI']
# groupnames = ['_BIRDS', '_MAMMALS', '_AMPHIBIANS', '_FISHES', '_CARTILAGINOUS FISHES', '_INSECTS', '_CRUSTACEANS', '_MOLLUSCS', '_PLANTS', '_FUNGI']


def load_names(groupnames,path):
    data = dict()
    print("-"*4,timestamp(),"-"*4)
    for index,name in enumerate(groupnames):
        pathname = path+"/_"+name+".shp"
        timer()
        try:
            db = gpd.read_file(pathname)
        except:
            print("Could not load",pathname)
            continue
        def get_color(cat):
            return categories.index(cat)
        db["color"]=db["category"].apply(get_color)
        def get_area(shape):
            return shape.area
        db["origin"]=name
        db.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        db=db.explode()
        db.index.droplevel(0)
        #print(db)
        #db.reset_index(drop=True,inplace=True)
        #print(list(db.index.values) )
        #print(db.index)
        db["area"]=db["geometry"].apply(get_area)
        db = db.sort_values(["color","area"],ascending=[True,False])
        #db.drop("area",inplace=True,axis=1)
        db.reset_index(drop=True,inplace=True)
        # if("_" not in name and name in "FISHESMAMMALSBIRDSPLANTS"):
            # #others are simplified 0.2
            # db["geometry"]=db["geometry"].simplify(0.3)
            # db.to_file(path+"/_"+name+".shp")
        print(timerstring(),"loaded %i/%i"%(index+1,len(groupnames)),pathname,len(db))
        # db=db.explode()
        #db.reset_index(drop=True,inplace=True)
        data[name]=db
        del db
    return data
    
timer(2)
path="databases/SMALLER_AGGREGATED_DATA"
aggregated_data = load_names(groupnames,path)
print(timerstring(2),"Finished loading all available aggregated data")
for entry in aggregated_data.values():
    print(entry)

timer(2)
path="databases/SMALLER_DATABASE_CLEAN_2"
alldata = load_names(groupnames,path)
print(timerstring(2),"Finished loading all habitat data")
for entry in alldata.values():
    print(entry)


import dash_table
def generate_table(dataframe, extinction_classes, max_rows=10):
    dataframe = dataframe[dataframe['category'].isin(extinction_classes)]
    dataframe = dataframe.sort_values(["color","area"],ascending=[False,True])
    selection = ["binomial","kingdom","phylum","class","order_","family","category"]
    limit = dataframe.columns
    selection = [x for x in selection if x in limit]
    dataframe=dataframe.filter(selection+["color"]).drop_duplicates(ignore_index=True)
    
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col.center(24)) for col in selection])
            ),
            html.Tbody([
                html.Tr([html.Td(dataframe.iloc[i][col].center(24)) 
                    for col in selection 
                ],id="ex%i"%(dataframe.iloc[i]["color"]+1)
                    )for i in range(min(len(dataframe),max_rows))
            ])
        ])
    # return dash_table.DataTable(
    # data=dataframe,
    # columns=[{'id': c, 'name': c} for c in dataframe.columns],
    # page_action='none',
    # style_table={'height': '300px', 'overflowY': 'auto'}
    # )



def recalculate_intersection(point_coords, selected_name):
    point = gpd.GeoSeries(Point(point_coords))
    point=gpd.GeoDataFrame(geometry=point)
    point.set_crs(epsg=4326,inplace=True)
    # print("Point's crs:",point.crs)
    # print(selected_categories)
    # relevant_data = alldata.loc[alldata["category"].isin(selected_categories)]
    #intersection.reset_index(inplace=True,drop=True)
    #intersection = alldata[selected_name].explode()
    intersection = gpd.sjoin(alldata[selected_name], point, op='intersects')
    # intersection=intersection.explode()
    # intersection = gpd.sjoin(intersection, point, op='intersects')
    #intersection.reset_index(inplace=True,drop=True)
    print("Intersection:",len(intersection))
    print(intersection.head(20))
    print("Calculations done")
    return intersection
    
    


def update_map_agg(geodata,levels):
    def get_color(cat):
        return palette.index(cat)
    # print(levels)
    geodata = geodata[geodata['category'].isin(levels)]
    geodata.reset_index(inplace=True,drop=True)
    geodata["index"]=geodata.index
    #geodata["identifier"]="Lobster"
    #geodata["id_type"]="order_"
    # columns = ["binomial","kingdom","phylum","class","order_","family","genus","category"]
    # columns = ["identifier","id_type","category"]
    columns = ["category","counter","origin"]
    def get_full_name(color):
        return cat_names[color]
    geodata["category"]=geodata["color"].apply(get_full_name)
    
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
    #fig.update_layout(clickmode='event+select')
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

    # geodata=geodata.filter(["color","geometry","category"])
    # print(levels)
    geodata = geodata[geodata['category'].isin(levels)]
    geodata.reset_index(inplace=True,drop=True)
    geodata["index"]=geodata.index
    columns = ["category","binomial","origin","phylum","class","order_","family","genus"]
    def get_full_name(color):
        return cat_names[color]
    geodata["category"]=geodata["color"].apply(get_full_name)
    
    # geodata=geodata.explode()
    show = {c:True for c in columns}
    show["color"]=False
    show["index"]=False
    #print(geojson.dumps(parsed, indent=4))
    print("Wanna draw=")
    print(len(geodata))
    print(geodata)
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
    #fig.update_layout(clickmode='event+select')
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
    point = gpd.GeoSeries(Point(crosshair))
    point=gpd.GeoDataFrame(geometry=point)
    point.set_crs(epsg=4326,inplace=True)
    x,y=crosshair
    #lat = [x],lon = [y], 
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
    html.Div(id="bigdiv",children=[
        dcc.Graph(id="map_graph",config={'displayModeBar': False}),
        html.Img(id="cursor_center",src="assets/selector.png"),
        html.Div(children=[
        
            html.Label("yes",id="update_node",style = dict(display='none')),
            html.Label(id="work_node",style = dict(display='none')),
            html.Label(id="i1",style = dict(display='none')),
            html.Label(id="i2",style = dict(display='none')),
            html.Label("Loading databases...",id="instructions"),
            html.Div(children=["Current database:",html.Label(id="selected_database_text")]),
            html.Div(children=[html.Button(dname, id=dname, n_clicks=0, disabled=not(dname in aggregated_data)) for dname in groupnames]),
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

def check_context(ctx):
    if(ctx.triggered==None):
        return []
    else:
        return [trig['prop_id'].split('.')[0] for trig in ctx.triggered]


from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


    
@app.callback(
    Output("selected_database_text","children"),
    Output("animal_type","children"),
    *(Input(dbname,"n_clicks") for dbname in groupnames)
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

@app.callback(
    Output("mouse_coord","children"),
    Input("map_graph","relayoutData"))
def update_location(relayoutData):
    print("Relayout data",relayoutData)
    if(relayoutData and 'mapbox.center' in relayoutData):
        y=relayoutData["mapbox.center"]["lon"]
        x=relayoutData["mapbox.center"]["lat"] 
    # if(relayoutData and 'mapbox._derived' in relayoutData):
        # x,y=relayoutData["mapbox._derived"]["coordinates"][0]
        # xx,yy=relayoutData["mapbox._derived"]["coordinates"][2]
        # x=(float(x)+float(xx))/2
        # y=(float(y)+float(yy))/2
        # x,y=y,x
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
    Input("mouse_coord","children"),
    State("selection_brag", "children"),
    State("extinction_classes","values")
)
def update_selection(selected_database_name,n_clicks,mouse_coords,current_selection,extinction_classes):
    y,x = (float(i) for i in mouse_coords.split())
    global selected_shapes
    ctx = check_context(dash.callback_context)
    print("Context for update selection:",ctx)
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
    if("crosshair_selection" in ctx):
        global current_mode
        if(current_selection=="the world"):
            current_mode="crosshair"
        else:
            current_mode="aggregate"
            selected_shapes = []
    print("Selected database:",selected_database_name)
    if(selected_database_name!=None):
        print("Current mode:",current_mode)
        if(current_mode=="crosshair"):
            point = (x,y)
            print("Clicked at",point)
            print(selected_database_name,selected_database_name in groupnames)
            sel=recalculate_intersection(point,selected_database_name)
            print("<<<<<<<<<<selection")
            print(sel)
            selected_shapes = sel
            return generate_table(selected_shapes,extinction_classes,1000), len(selected_shapes), "%.2f %.2f"%(x,y)
        else:
            if(ctx==["mouse_coord"]):
                raise PreventUpdate
            selected_animals = alldata[selected_database_name]
            return generate_table(selected_animals,extinction_classes,1000), len(selected_animals), "the world"
    else:
        raise PreventUpdate
    
    

import json
@app.callback(
    Output("i1","children"),
    Output('map_graph', 'figure'),
    Input('extinction_category', 'value'),
    Input("selected_database_text","children"),
    Input("selection_brag","children"),
    Input("mouse_coord","children")
)
def update_graph_selection(extinction_classes,selected_database_name,selection_text,mouse_coords):
    ctx = check_context(dash.callback_context)
    global unchanged_graph
    print("Selected db name:",selected_database_name)
    if(not selected_database_name):
        instruction = "For starters, select one database"
    else:
        instruction = "Updating graph, please wait"
    if(selection_text=="the world"):
        #if(ctx.triggered!=None and (ctx.triggered[0]['prop_id'].split('.')[0] not in ["selected_database_text","extinction_category"])):
        #    raise PreventUpdate
        #unchanged_graph=[]
        if(selected_database_name):
            graph=update_map_agg(aggregated_data[selected_database_name],extinction_classes)
            unchanged_graph=graph
            instruction = "Aggregated view\nClick Toggle Selection to switch"
        else:
            graph = dict()
            
    else:
        # if(not unchanged_graph):
            # graph=update_map_agg(aggregated_data[aggregated_data["origin"]==selected_database_name],classes)
            # unchanged_graph=[graph]
        if(len(selected_shapes)==0):
            print("NO SELECTED SHAPE DETECTED")
            return instruction, unchanged_graph
        y,x = (float(i) for i in mouse_coords.split())
        print("Sending %i selected shapes to graph..."%len(selected_shapes))
        gdf = selected_shapes
        print(gdf)
        graph = update_map_select(gdf,extinction_classes,(y,x))
        instruction = "Crosshair view\nShows animals under the Crosshair"
    return instruction, graph


# @app.callback(
    # Output("map_graph","figure"),
    # Input("work_node","children")
# )
# def start_working():
    # pass



@app.callback(
    Output("i2","children"),
    Input('map_graph', 'figure'))
def update_instructions_graph(fig):
    print("Entered Update Graph callback")
    print(bool(unchanged_graph),bool(len(selected_shapes)))
    #print(unchanged_graph)
    if(unchanged_graph):
        if(len(selected_shapes)==0):
            print("NO SELECTED SHAPE...")
            return "Updating graph, please wait"
        else:
            return "Updating graph, please wait"
    else:
        return "For starters, select one database"
        #raise PreventUpdate

@app.callback(
    Output("instructions","children"),
    Input("i1","children"),
    Input("i2","children"),
    Input("update_node","children"), 
    prevent_initial_call=True)
def update_instructions_funnel(i1,i2,u1):
    print("Entered I1I2 callback")
    print(i1,i2)
    ctx = check_context(dash.callback_context)
    print(ctx)
    if("i2" in ctx):
        return i2
    elif("i1" in ctx):
        return i1
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.layout=layout
    app.run_server(debug=True)