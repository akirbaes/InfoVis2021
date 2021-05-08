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
	
	
path="SIMPLIFIED_DATA"
has_data = False
alldata = None
counter = 0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS
            pathname =os.path.join(dirpath, name)
            print("Open",str(counter),pathname)
            counter+=1
            db = gpd.read_file(pathname)
            print(timerstring(),"Finished reading database")
            if(has_data==False):
                has_data=True
                alldata=db
            else:
                alldata=alldata.append(db)
			
            #print(timerstring(),"Merged databases")
            print("Elements:",alldata.size,"Shape:",alldata.shape)
# data.unary_union()
# print(timerstring(),"Unary union")
# gplt.choropleth(database,alpha=0.5)
# print(timerstring(),"Choroprep")
# plt.show()
# print(timerstring(),"Show")
# plt.clf()
                    
print(lapstring(),"Loading/Merging all files done")
surfaces = None
palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
names = ["Data defficient","Least concern", "Lower risk", "Near threatened", "Conservation dependent-", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
def generate_scheme(database):
    palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
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
    scheme=mc.EqualInterval(database["color"],k=len(palette))
    return scheme
    
timer()
laptime()
import alphashape
print(alldata.head())
scheme=generate_scheme(alldata)
print(lapstring(),"Scheme generated")
kingdom_data = alldata["kingdom"].unique()
for kingdom in kingdom_data:
    print("Aggregating",kingdom)
    kingdom_frame=alldata[alldata["kingdom"]==kingdom][["category","color","geometry"]]
    print(kingdom_frame.head())
    laptime()
    
    kingdom_frame.reset_index(inplace=True)
    kingdom_frame=kingdom_frame.dissolve(by="color")
    print(lapstring(),"Data dissolved")
    kingdom_frame=kingdom_frame.simplify(1)
    print(lapstring(),"Simplified",kingdom+".shp")
    #kingdom_frame.sort_values(by="color",axis=0,ascending=True,inplace=True)
    #print(lapstring(),"Sorted",kingdom+".shp")
    print(kingdom_frame.head())
    kingdom_frame.to_file("AGGREGATED_DATA/"+kingdom+".shp")
    print(lapstring(),"Saved",kingdom+".shp")

#category_dissolve=genus[["category","geometry"]].dissolve(by="category",as_index=False)
#print("\tHead\n",alldata.head())
#print("\tColor\n",alldata["color"])
#gplt.choropleth(alldata,alpha=0.7,hue="color",scheme=scheme)
#plt.show()
"""for entry in palette:
    print("Opening data",entry)
    surface = alldata[alldata["category"] == entry]
    
    print(timerstring(),"Selected")
    #surface = surface.unary_union()
    print(timerstring(),"Union")
    #percent = palette.index(surface["category"])/len(palette)-1
    #gplt.choropleth(surface,alpha=0.5)
    #print(timerstring(),"Plot")
"""
print("Done")