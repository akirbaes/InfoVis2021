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

database = gpd.read_file("REDLIST/MAMMALS/MAMMALS.shp")
#database = gpd.read_file("REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp")
#database = gpd.read_file("REDLIST/REPTILES_points/REPTILES_points.csv")

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

scheme=mc.FisherJenks(database["color"],k=len(palette))
gplt.choropleth(database,hue=database["color"],alpha=0.5, legend=True, scheme=scheme, legend_labels=names)
"""leg=ax1.get_legend()
for i,e in enumerate(palette):
    leg.get_texts()[i].set_text(names[i])"""
#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
#world.plot();

#gplt.polyplot(database)
#gplt.polyplot(world)
plt.show()
print("Finished showing the database at %s seconds"%(time.time()-start_time))