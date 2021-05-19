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
	
has_data = False
alldata = None



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

def get_area(entry):
    return entry.area

#path="SIMPLIFIED_DATA"
path="REDLIST"
total_count=0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")):
            total_count+=1
counter = 0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS
            counter+=1
            if(counter>=37):
                pathname =os.path.join(dirpath, name)
                print("[%i/%i]Open"%(counter,total_count),pathname)
                db = gpd.read_file(pathname)
                print(lapstring(),"Finished reading database")
                generate_color(db) #add "color" entry
                
                foldername = "ORDER_AGGREGATED_DATA/"
                try:os.mkdir(foldername)
                except:pass
                # print(list(db.columns))
                orders = db["order_"].unique()
                for index,order in enumerate(orders):
                    output = db[db["order_"]==order]
                    k = output["kingdom"].iat[0]
                    p = output["phylum"].iat[0]
                    c = output["class"].iat[0]
                    outputname = k+"_"+p+"_"+c+"_"+order+"_"+name
                    
                    output=output.explode()
                    output["area"]=output["geometry"].apply(get_area)
                    output=output[output["area"]>0.05]
                    output["geometry"]=output.simplify(0.1)
                    
                    for type in "marine","terrestial","freshwater":
                        outputname = k+"_"+p+"_"+c+"_"+order+"_"+type+"_"+name
                        selection = output[output[type]=="true"]
                        selection = selection.filter(["category",'color', 'geometry'])
                        if(len(selection)==0):
                            continue
                        print(len(selection),outputname,"%i/%i"%(index+1,len(orders)) if len(orders) else "")
                        selection=selection.dissolve(by="color")
                        selection.to_file(foldername+outputname)
                        print(lapstring(),"Output to ",foldername+outputname)
                        del selection
                    
                    # output = output.filter(["category",'color', 'geometry'])
                # print(len(color_output),outputname,"%i/%i"%(index+1,len(orders)) if len(orders) else "")
                # output=output.dissolve(by="color")
                # output.to_file(foldername+outputname)
                # print(lapstring(),"Output to ",foldername+outputname)
                # del output

                    
print(timerstring(),"Aggregating all files done")
print("Done")