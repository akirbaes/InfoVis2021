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
import time

start_time = time.time()




# filename="REDLIST/MAMMALS/MAMMALS.shp"
# filename="AGGREGATED_DATA/_agg_MAMMALS.shp"
# filename="REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp"
# filename="REDLIST/REPTILES_points/REPTILES_points.csv"
# filename="REDLIST/Fishes/BONEFISH_TARPONS/BONEFISH_TARPONS.shp"
# filename="SIMPLIFIED_DATA/BONEFISH_TARPONS.shp"
filename = "ORDER_AGGREGATED_DATA/ANIMALIA_CHORDATA_ACTINOPTERYGII_ALBULIFORMES_BONEFISH_TARPONS.shp"
filename = "ORDER_AGGREGATED_DATA/ANIMALIA_CHORDATA_MAMMALIA_CHIROPTERA_MAMMALS.shp"
database = gpd.read_file(filename)

print("Finished reading database at %s seconds"%(time.time()-start_time))

start_time = time.time()

palette=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
def get_color(cat):
    return palette.index(cat)

database["color"]=database["category"].apply(get_color)
print(database.color.head())
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

#database["color"]=7

#database.plot();
#category = database['category']
#scheme = mapclassify.Quantiles(category, k=5)

#print(database["category"].unique())
#database=database["binomial"]=="Vulpes lagopus"
#selection=database["category"]=="DD"
#database.where(selection, inplace=True)
database.sort_values(by="color",axis=0,ascending=True,inplace=True)
# database.plot()
# plt.show()
# database = database.to_crs("EPSG:3395")
# database.plot()
# plt.show()
print(database.crs)
fig, ax = plt.subplots()


scheme=mc.EqualInterval(database["color"],k=len(palette))
"""leg=ax1.get_legend()
for i,e in enumerate(palette):
    leg.get_texts()[i].set_text(names[i])"""
#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
#world.plot();
from shapely.geometry import Point, Polygon
pts = list((long,lat) for long in (-180,0,180) for lat in (-90,0,90))
geom=list((Point((float(long),float(lat))) for long,lat in pts))
print(pts)
db = gpd.GeoDataFrame(geometry=geom)
ax.set_aspect('equal')
gplt.choropleth(database,hue=database["color"],alpha=0.5, legend=True, scheme=scheme, legend_labels=names, ax=ax, legend_kwargs={"loc":'lower left'})
# gplt.pointplot(db, color="red", markersize=1,ax=ax)
# db.plot(ax=ax, marker=',', color='red', markersize=1,zorder=10)

x = [-180,-180,180,180]
y = [-90,90,-90,90]
plt.scatter(x=x,y=y, marker=',', color='red', linewidths=0,s=0.75,zorder=10)

#gplt.polyplot(database)
#gplt.polyplot(world)
plt.show()
print("Finished showing the database at %s seconds"%(time.time()-start_time))