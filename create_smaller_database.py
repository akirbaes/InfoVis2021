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
import colorama
import os
colorama.init()
start_time = time.time()

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
    
#database = gpd.read_file("REDLIST/MAMMALS/MAMMALS.shp")
#database = gpd.read_file("REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp")
#database = gpd.read_file("REDLIST/REPTILES_points/REPTILES_points.csv")
path="REDLIST"#/Fishes/BONEFISH_TARPONS"
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")):
            pathname =os.path.join(dirpath, name)
            print("Open",pathname)
            db = gpd.read_file(pathname)
            print(timerstring(),"Finished reading database")
            data = db[['binomial','kingdom','phylum','class','order_','family','genus','category']]#,'geometry' would preserve geometry
            data=gpd.GeoDataFrame(data, geometry=db.simplify(1.5))
            print(timerstring(),"Simplified database")
            data.to_file("SIMPLIFIED_DATA/"+name)
            print(timerstring(),"Output database at "+"SIMPLIFIED_DATA/"+os.path.basename(name))
            # data.unary_union()
            # print(timerstring(),"Unary union")
            # gplt.choropleth(database,alpha=0.5)
            # print(timerstring(),"Choroprep")
            # plt.show()
            # print(timerstring(),"Show")
            # plt.clf()
                    
print("All done")
"""
for database in (data,db):
    start_time = time.time()
    print(database.head())
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
    gplt.choropleth(database,hue=database["color"],alpha=0.5, legend=True, legend_kwargs={"loc":'lower left'}, scheme=scheme, legend_labels=names)
    #world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #world.plot();

    #gplt.polyplot(database)
    #gplt.polyplot(world)
    plt.show()
    print("Finished showing the database at %s seconds"%(time.time()-start_time))
    input("Input to clear")
    plt.clf()
"""