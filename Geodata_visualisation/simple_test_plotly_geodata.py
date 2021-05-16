import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
import json
import pprint
categories=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
cat_colors=[(212,212,212),(100,100,100),(70,30,89),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
color_of_cat = {cat:"#"+"".join([hex(x)[-2:] for x in cat_colors[id]]) for (id,cat) in enumerate(categories)}
# color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
print(color_of_cat)

#geodf = gpd.read_file("assets/_agg_AMPHIBIANS.shp")
# geodf = gpd.read_file("assets/_agg_CLUPEIFORMES.shp").explode()
geodf = gpd.read_file("assets/_agg_CLUPEIFORMES.shp").explode()
#geodf=geodf.explode()
# geodf = gpd.read_file("assets/BONEFISH_TARPONS.shp")
#geodf = gpd.read_file("SIMPLIFIED_DATA/BONEFISH_TARPONS.shp") # BONEFISH_TARPONS MAMMALS
geodf.to_file("assets/TRY_SIMPLE.shp")
palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print("Geometry's first:",geodf["geometry"][0])


discrete_map = {i:"red" for i in range(len(palette))}

def get_color(cat):
    return palette.index(cat)
#geodf["color2"]=geodf["category"].apply(get_color)
#geodf["number"]=geodf.index
locs = list(geodf.index)
print(geodf.head)

geodf.to_file("assets/output.json", driver='GeoJSON')
with open("assets/output.json") as geofile:
	j_file = json.load(geofile)
#pprint.pprint(j_file)

#simpledf = geodf[["color","number"]]


simpledf = pd.read_csv("assets/_agg_CLUPEIFORMES.csv",
                   dtype={"color": str})
print(simpledf.head())
fig = px.choropleth_mapbox(simpledf, 
    geojson=j_file,
    locations="color",
    mapbox_style="carto-positron",
    color="category",
    color_discrete_map=color_of_cat
    )
    
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()