#aggregate database created by part 2 fix
import geopandas as gpd
import pandas as pd
import time
from datetime import datetime
import colorama
import os
from shapely.geometry import Polygon
from simpledbf import Dbf5
colorama.init()
#Fix the heavy dbf
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

path="SMALLER_DATABASE"
outpath="SMALLER_DATABASE_CLEAN"
try:os.mkdir(outpath)
except:pass
counter=0

def count_all(path):
    counter=0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".shp")):
                counter+=1
    return counter
max_counter = count_all(path)
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if (name.endswith(".shp")):
            
            pathname =os.path.join(dirpath, name)
            """Load the database"""
            timer(1)
            print("-"*4,timestamp(),"-"*4)
            print("Open %i/%i "%(counter,max_counter),pathname)
            counter+=1
            timer()
            db = gpd.read_file(pathname)
            print(timerstring(),"read database,",str(len(db))," elements")
            
            db = db.filter(['binomial','kingdom','phylum','class','order_','family','genus','category',"marine","terrestial","freshwater","geometry"])
            db=db.dissolve(by="binomial",as_index=False,aggfunc='first')
            print(timerstring(),"Aggregated down to",len(db))
            print(db)
            outputfile = outpath+"/"+name
            db.to_file(outputfile)
            print(timerstring(),"output to",outputfile)            #selection=selection.sort_values(by=["category"])
            

print("-"*4,timestamp(),"-"*4)
print(timerstring(2),"all done")
            
            
            