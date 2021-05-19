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

def load_all_data(path):
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                print("Open",str(counter),pathname)
                counter+=1
                db = gpd.read_file(pathname)
                db["origin"]=name
                # print(timerstring(),"Finished reading database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db,ignore_index=False)
                print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata

#aggregated_data = gpd.read_file("AGGREGATED_DATA/_agg_LOBSTERS.shp")
path="assets/Light_server/SIMPLIFIED_DATA"
path="assets/Mammals_server/SIMPLIFIED_DATA"
alldata = load_all_data(path)
print("Finished loading all simplified habitat data")
print(alldata)

#aggregated_data = gpd.read_file("AGGREGATED_DATA/_agg_LOBSTERS.shp")
path="assets/Light_server/AGGREGATED_DATA"
path="assets/Mammals_server/AGGREGATED_DATA"
aggregated_data = load_all_data(path)
print("Finished loading all available aggregated data")
print(aggregated_data)



categories=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
palette=categories
cat_names = ["Data defficient","Least concern", "Lower risk", "Near threatened", "Conservation dependent-", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
cat_colors=[(212,212,212),(100,100,100),(90,70,100),(70,3,89),(60,30,100),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
cat_colors=list("#"+"".join((("{:02x}".format(c) for c in col))) for col in cat_colors)

color_of_catid = {id:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_category = {cat:cat_colors[id] for (id,cat) in enumerate(cat_names)}


def generate_table(dataframe, max_rows=10):
    selection = ["binomial","kingdom","phylum","class","order_","family","genus","category"]
    limit = dataframe.columns
    selection = [x for x in selection if x in limit]
    dataframe=dataframe.filter(selection)
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in selection])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in selection 
                ])for i in range(min(len(dataframe),max_rows))
            ])
        ])


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

def recalculate_intersection(point_coords):
    #global intersection
    point = gpd.GeoSeries(Point(point_coords))
    point=gpd.GeoDataFrame(geometry=point)
    point.set_crs(epsg=4326,inplace=True)
    # print("Point's crs:",point.crs)
    # print(selected_categories)
    # relevant_data = alldata.loc[alldata["category"].isin(selected_categories)]
    intersection = gpd.sjoin(alldata, point, op='intersects')
    print("Intersection:",len(intersection))
    print(intersection.head(20))
    return intersection
    
    


def update_map_agg(geodata,levels,terrain,crosshair):
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
    def get_file_name(origin):
        return origin[5:-4]
    geodata["origin"]=geodata["origin"].apply(get_file_name)
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
            opacity=1
            )
    else:
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["origin"],
            opacity=0.8
            )
    fig.update_layout(uirevision="don't update")
    
    x,y=crosshair
    # fig.add_shape(type="line",x0=x-1, y0=y, x1=x+1, y1=y)
    # fig.add_shape(type="line",x0=x, y0=y-1, x1=x, y1=y+1)
    fig.add_scattermapbox(lat = [x],lon = [y])
    return fig
    

def update_map_select(geodata,levels,terrain,crosshair):
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
    def get_file_name(origin):
        return origin[5:-4]
    geodata["origin"]=geodata["origin"].apply(get_file_name)
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
            opacity=0.5
            )
    else:
        fig = px.choropleth_mapbox(geodata,
            geojson=geodata.geometry,
            locations=geodata["index"],
            color=geodata["category"],
            color_discrete_map=color_of_category,
            mapbox_style="carto-positron",
            hover_data=show,
            hover_name=geodata["binomial"],
            opacity=0.5
            )
    # fig.update_geos(fitbounds="locations")
    fig.update_layout(uirevision="don't update")
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
    fig.add_scattermapbox(lat = [x],lon = [y])
    # fig.add_shape(type="line",x0=x-1, y0=y, x1=x+1, y1=y)
    # fig.add_shape(type="line",x0=x, y0=y-1, x1=x, y1=y+1)
    
    return fig

plotlyConfig = {'topojsonURL':'http://127.0.0.1:%i/assets/'%5500} 
class_names = 'MAMMALIA', 'JUNGERMANNIOPSIDA', 'CHAROPHYACEAE', 'SARCOPTERYGII', 'CLITELLATA', 'LYCOPODIOPSIDA', 'BRANCHIOPODA', 'MAGNOLIOPSIDA', 'CHONDRICHTHYES', 'AMPHIBIA', 'INSECTA', 'BIVALVIA', 'ACTINOPTERYGII', 'AGARICOMYCETES', 'HYDROZOA', 'BRYOPSIDA', 'ANTHOZOA', 'CEPHALASPIDOMORPHI', 'LILIOPSIDA', 'MYXINI', 'GASTROPODA', 'LECANOROMYCETES', 'POLYPODIOPSIDA', 'MARCHANTIOPSIDA', 'REPTILIA', 'AVES', 'MALACOSTRACA'
# class_names = ['TETRAODONTIFORMES',"CHIMAERIFORMES"]
multiselect_options = [{"label":classe,"value":classe} for classe in class_names]
multiselect_values = class_names[:]

#checklist_options  = [{"label":html.Mark(children=cat_names[i],id=cat),"value":cat} for i,cat in enumerate(categories)]
checklist_options  = [{"label":cat_names[i],"value":cat} for i,cat in enumerate(categories)]
checklist_values = categories[:]

habitat_values = ["Marine","Terestial","Freshwater"]
habitat_options = [{"label":hab,"value":hab} for hab in habitat_values]

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
        dcc.Input(id='longitude', value="0", type='number'),
        dcc.Input(id='latitude', value="0", type='number')
    ]),
    html.Button('Submit', id='submit_coords', n_clicks=0),
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
    html.Label('Habitat type'),
    dcc.Checklist(
        options=habitat_options,
        value=habitat_values,
        id="habitat_type"
    ),
    html.Label('Aggregation mode'),
    dcc.Checklist(
        options=[{"label":"Aggregate","value":"aggregate"}],
        value=["aggregate"],
        id="aggregate_toggle"
    ),
    html.Div(children="Table area",id="table_to_fill"),
    dcc.Store(id="intermediate_value")
])

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
    
    

@app.callback(
    Output('aggregate_toggle', 'value'),
    Input('submit_coords', 'n_clicks')
    )
def start_looking_at_point(nclick):
    print("Nclick:",nclick)
    if nclick is 0:
        raise PreventUpdate
    return []

@app.callback(
    Output('intermediate_value', 'data'),
    Output('table_to_fill', 'children'),
    Output('animals_count', "children"),
    Input('map_graph', 'selectedData'),
    Input('longitude','value'),
    Input('latitude','value')
)
def update_selection(selectedData,longitude,latitude):
    print(dash.callback_context.triggered)
    
    
    if(selectedData and selectedData["range"]):
        ranges = selectedpoints_local['range']
        selection_bounds = {'x0': ranges['x'][0], 'x1': ranges['x'][1],
                            'y0': ranges['y'][0], 'y1': ranges['y'][1]}
        point = (ranges['x'][0],ranges['y'][0])
    else:
        #raise PreventUpdate
        point = (float(longitude),float(latitude))
    print("Clicked at",point)
    sel=recalculate_intersection(point)
    sel.reset_index(inplace=True,drop=True)
    global selected_shapes
    selected_shapes = sel
    sel = sel.to_json()
    # print("Received selection:")
    # print(sel)
    return sel, generate_table(selected_shapes,10), len(selected_shapes)
    

import json
#from shapely import MultiPolygon
@app.callback(
    Output('map_graph', 'figure'),
    Input('intermediate_value', 'data'),
    Input('extinction_category', 'value'),
    Input('habitat_type', 'value'),
    Input('longitude','value'),
    Input('latitude','value'),
    Input('aggregate_toggle','value')
)
def update_graph_selection(selection_shapes,classes,habitats,longitude,latitude,aggregate_toggle):
    point=(float(longitude),float(latitude))
    # if(not selection_shapes):
    if("aggregate" in aggregate_toggle):
        graph=update_map_agg(aggregated_data,classes,habitats,point)
        # raise PreventUpdate
    else:
        jj = json.loads(selection_shapes)
        #print("Json of thing=",jj["features"])
        #df =  pd.DataFrame.from_dict(jj["features"])
        #print(df)
        #gdf = gpd.GeoDataFrame(df, geometry='geometry')
        
        #gdf.set_crs(epsg=4326,inplace=True)
        #print("Geodata received size",len(gdf))
        gdf = selected_shapes
        graph = update_map_select(gdf,classes,habitats,point)
    return graph

@app.callback(
    Output(component_id='selected_classes', component_property='value'),
    Input(component_id='select_all_classes', component_property='n_clicks')
)
def set_all_classes(ignore):
    return class_names[:]



if __name__ == "__main__":
    app.run_server(debug=True)