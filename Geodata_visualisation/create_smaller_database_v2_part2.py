#load db created by create_smaller_database_v2 and group them by database name
import geopandas as gpd
import pandas as pd
import time
from datetime import datetime
import colorama
import os
from shapely.geometry import Polygon
colorama.init()
#Delete small islands in database<0.1 area, simplify 0.1
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
categories=['DD', 'LC', 'LR/lc', 'LR/cd', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
database_names = {("class",'AVES'): 'BIRDS', 
("class",'MAMMALIA'): 'MAMMALS', 
("class",'AMPHIBIA'): 'AMPHIBIANS', 
("class",'ACTINOPTERYGII'): 'FISHES', 
("class","CHONDRICHTHYES"):"CARTILAGINOUS FISHES",
("class",'INSECTA'): 'INSECTS', 
("class",'MALACOSTRACA'): 'CRUSTACEANS', 
("phylum",'MOLLUSCA'): 'MOLLUSCS', 
("kingdom","PLANTAE"): 'PLANTS', 
("kingdom","FUNGI"): 'FUNGI'}

path="SMALLER_DATA"
outpath="SMALLER_DATABASE"
try:os.mkdir(outpath)
except:pass
counter=1

start = False
count_points = False
print(list(database_names.values()))
for index,group_name in enumerate(database_names.values()):
    """if(group_name=="CRUSTACEANS"):
        start=True
    if(start==False or group_name=="CRUSTACEANS"):
        continue"""
    print("-"*4,timestamp(),"-"*4)
    print("Reading for %i/%i"%(index,len(database_names)),group_name)
    has_data = False
    alldata = None
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if(name.startswith(group_name) and name.endswith(".shp")):
                pathname =os.path.join(dirpath, name)
                """Load the database"""
                print("Open",pathname)
                timer()
                db = gpd.read_file(pathname)
                print(timerstring()+" read database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db,ignore_index=True)
                counter+=1
    timer()
    
    
    def get_color(cat):
        return categories.index(cat)
    alldata["color"]=alldata["category"].apply(get_color)
    def get_area(shape):
        return shape.area
    alldata["area"]=alldata["geometry"].apply(get_area)
    alldata.sort_values(["color","area"],ascending=[True,False],inplace=True,ignore_index=True)
    alldata.drop("color",axis=1,inplace=True)
    alldata.drop("area",axis=1,inplace=True)
    outputfile = outpath+"/"+group_name+".shp"
    alldata.to_file(outputfile)
    print(timerstring(),"output",outputfile)
    del alldata