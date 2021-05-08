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
timer()
	
path="SIMPLIFIED_DATA"
has_data = False
alldata = None
counter = 0



palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
names = ["Data defficient","Least concern", "Lower risk", "Near threatened", "Conservation dependent-", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]

def generate_color(database,scheme=False):
    palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
    names = ["Data defficient","Least concern", "Lower risk", "Near threatened", "Conservation dependent-", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
    categories = database["category"].unique()
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
    def get_color(cat):
        return palette.index(cat)
    #print(categories)
    #print(palette)
    #print(len(categories),len(palette))
    database["color"]=database["category"].apply(get_color)
    #database.sort_values(by="color",axis=0,ascending=True,inplace=True)
    if(scheme):
        scheme=mc.EqualInterval(database["color"],k=len(palette))
        return scheme


for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS
            pathname =os.path.join(dirpath, name)
            print("Open",str(counter),pathname)
            counter+=1
            db = gpd.read_file(pathname)
            print(lapstring(),"Finished reading database")
            generate_color(db) #add "color" entry
            
            for column in ['binomial','kingdom','phylum','class','order_','family','genus']:
                db.drop(column, inplace=True, axis=1)
            db=gpd.GeoDataFrame(db[["category","color"]], geometry=db.simplify(3))
            print(lapstring(),"Pre-simplified")
            db=db.dissolve(by="color")
            print(lapstring(),"Data dissolved")
            db=gpd.GeoDataFrame(db[["category"]], geometry=db.simplify(1))
            print(lapstring(),"Simplified")
            print(db.head())
			
            db.to_file("AGGREGATED_DATA/"+"_agg_"+name)
            print(lapstring(),"Output to ","AGGREGATED_DATA/"+"_agg_s3_"+name)
            print("Elements:",db.size,"Shape:",db.shape)
# data.unary_union()
# print(timerstring(),"Unary union")
# gplt.choropleth(database,alpha=0.5)
# print(timerstring(),"Choroprep")
# plt.show()
# print(timerstring(),"Show")
# plt.clf()
                    
print(timerstring(),"Aggregating all files done")
print("Done")