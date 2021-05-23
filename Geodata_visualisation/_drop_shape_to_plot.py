import geoplot as gplt
import geopandas as gpd
import geoplot.crs as gcrs
import imageio
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import mapclassify as mc
import numpy as np
import mapclassify as mc
import sys
import os

import time
from datetime import datetime
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


g_interior_shapes, g_exterior_shapes, g_interior_points, g_exterior_points = 0,0,0,0

def count_shapes(db):
    interior_shapes = 0
    exterior_shapes = 0
    interior_points = 0
    exterior_points = 0
    for shape in db["geometry"]:
        if(shape.geom_type == 'MultiPolygon'):
            iter = shape
        elif(shape.geom_type == 'Polygon'):
            iter=[shape]
        else:
            print(shape.geom_type)
        exterior_shapes+=len(iter)
        for poly in iter:
            exterior_points += len(poly.exterior.coords)
            interior_shapes+=len(poly.interiors)
            for interior in poly.interiors:
                interior_points += len(interior.coords)
        
    global g_interior_shapes, g_exterior_shapes, g_interior_points, g_exterior_points
    g_interior_shapes += interior_shapes
    g_exterior_shapes += exterior_shapes
    g_interior_points += interior_points
    g_exterior_points += exterior_points
    return exterior_shapes, exterior_points, interior_shapes, interior_points 
    
    
filename = sys.argv[1]
print("Reading",filename)
timer()
database = gpd.read_file(filename)
readtime = timer()
print(readtime,"s","read database")

    
exterior_shapes, exterior_points, interior_shapes, interior_points = count_shapes(database)

print(len(database),"elements")
try:
    print(len(database["binomial"].unique()),"species")
except: pass
print("total interior_shapes poly:",  interior_shapes)
print("total exterior_shapes poly:",  exterior_shapes)
print("total  poly:",  interior_shapes+exterior_shapes)
print("total interior_points:",        interior_points)
print("total exterior_points:",        exterior_points)
print("total points:",        interior_points+exterior_points)

print("%i points, %i exterior polys, %i interior polys"%(interior_points+exterior_points,exterior_shapes, interior_shapes))



categories=['DD', 'LC', 'LR/lc', 'LR/cd', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]

cat_names = ["Data defficient","Least concern", "Lower risk", "Conservation dependent", "Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
cat_colors=[(212,212,212),(100,100,100),(90,70,100),(70,3,89),(60,30,100),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
cat_colors=list("#"+"".join((("{:02x}".format(c) for c in col))) for col in cat_colors)

color_of_catid = {id:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
color_of_category = {cat:cat_colors[id] for (id,cat) in enumerate(cat_names)}
palette=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
names = ["Data defficient","Least concern", "Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
def get_color(cat):
    return palette.index(cat)

database["color"]=database["category"].apply(get_color)
# print(database.color.head())
categories = database["category"].unique()
print(categories)
print(len(categories))

to_remove = list()
if(len(categories)!=len(palette)):
    for index,element in enumerate(palette):
        if element not in categories:
            to_remove.append(index)

shift=0
for index in to_remove:
    palette.pop(index+shift)
    names.pop(index+shift)
    shift-=1

database.sort_values(by="color",axis=0,ascending=True,inplace=True)
print("crs=",database.crs)
fig, ax = plt.subplots()


scheme=mc.EqualInterval(database["color"],k=len(palette))

# from shapely.geometry import Point, Polygon
# pts = list((long,lat) for long in (-180,0,180) for lat in (-90,0,90))
# geom=list((Point((float(long),float(lat))) for long,lat in pts))
# print(pts)
# db = gpd.GeoDataFrame(geometry=geom)
ax.set_aspect('equal')
gplt.choropleth(database,hue=database["color"],alpha=0.5, legend=True, scheme=scheme, legend_labels=names, ax=ax, legend_kwargs={"loc":'lower left'})
foldername = "screenshots/"
imagename="-".join(filename.split("\\")[-2:])+".png"
try: os.mkdir(foldername)
except:pass
timer()
dp=600
plt.savefig(foldername+imagename,dpi=dp,transparent=True)
print(timerstring(),"Saved",imagename)
plt.clf()
#plt.show()
input("Press enter to quit")