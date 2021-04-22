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
from shapely.geometry import Point, Polygon

start_time = time.time()

#database = gpd.read_file("REDLIST/MAMMALS/MAMMALS.shp")
#database = gpd.read_file("REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp")
#database = gpd.read_file("REDLIST/REPTILES_points/REPTILES_points.csv")
database = gpd.read_file("REDLIST/FreshWater_GROUP_points/FW_GROUP_points_edit_2.csv")

print("Finished reading database at %s seconds"%(time.time()-start_time),flush=True)

start_time = time.time()

palette=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
def get_color(cat):
    return palette.index(cat)

categories = database["category"].unique()
print("Uniques:",len(categories),categories)

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


print("Palettes:",len(palette))
print("Names:",len(names))
database["color"]=database["category"].apply(get_color)

unicol = database["color"].unique()
print("Unicol:",len(unicol),unicol)

database["geometry"]=[Point((float(x),float(y))) for x,y in zip(database["longitude"],database["latitude"])]
print(database.head())
#database=database["binomial"]=="Vulpes lagopus"
#selection=database["category"]=="DD"
#database.where(selection, inplace=True)
database.sort_values(by="color",axis=0,ascending=True,inplace=True)

print("Scheme: k=",len(palette))
scheme=mc.EqualInterval(database["color"],k=len(palette))
print(scheme)
print(database.head())
gplt.pointplot(database,hue="color",legend=True, legend_labels=names,scheme=scheme)
plt.show()
#gplt.pointplot(database,hue=database["color"],alpha=0.5, legend=True, scheme=scheme, legend_labels=names)
#np.isfinite(database).all(1)
print("Finished showing the database at %s seconds"%(time.time()-start_time))