import geopandas as gpd
import pandas as pd
import time
from datetime import datetime
import colorama
import os
from shapely.geometry import Polygon
from simpledbf import Dbf5
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

database_names = {
("phylum",'MOLLUSCA'): 'MOLLUSCS'
}

#database = gpd.read_file("REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp")
#database = gpd.read_file("REDLIST/REPTILES_points/REPTILES_points.csv")
path="REDLIST"#/Fishes/BONEFISH_TARPONS"
# path = "REDLIST/MAMMALS/"
outpath="SMALLER_DATA"
try:os.mkdir(outpath)
except:pass

def count_all(path):
    counter=0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".shp")):
                counter+=1
    return counter
max_counter = count_all(path)
count_points = False

def check_if_worth_opening(filename):
    filename=filename[:-4]+".dbf"
    df = Dbf5(filename).to_dataframe()
    
    for column,value in database_names.keys():
        if(len(df[df[column]==value])>0):
            del df
            return True
    return False

counter=1
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if (name.endswith(".shp")):
            pathname =os.path.join(dirpath, name)
            if not(check_if_worth_opening(pathname)):
                print("Skipped",name)
                continue
            """Load the database"""
            print("-"*4,timestamp(),"-"*4)
            print("Open %i/%i "%(counter,max_counter),pathname)
            counter+=1
            timer()
            db = gpd.read_file(pathname)
            print(end=timerstring()+" read database, ")
            print(end=str(len(db))+" elements, ")
            db.drop(["id_no","presence","origin","seasonal","compiler","yrcompiled","subpop","source","tax_comm","dist_comm","legend"],axis=1,inplace=True)
            # data = db[["citation",'binomial','kingdom','phylum','class','order_','family','genus','category',"marine","terrestial","freshwater","SHAPE_Leng","SHAPE_Area","geometry"]]#,'geometry' would preserve geometry
            
            """###Preprocessing###"""
            db=db.explode()
            def get_pointlenght(geom):
                if geom.type == 'Polygon': #because we used explode first
                    exterior_coords = len(geom.exterior.coords)
                    interior_coords = 0
                    for interior in geom.interiors:
                        interior_coords += len(interior.coords)
                return exterior_coords+interior_coords
            print(len(db),"polygons,")
            if(count_points):
                pointscount = db["geometry"].apply(get_pointlenght).sum()
                print(pointscount,"points")
            timer()
            
            """Remove small areas"""
            def get_area(geom):
                return geom.area
            db["area"]=db["geometry"].apply(get_area)
            arealimit=0.05
            db=db[db["area"]>=arealimit]
            db=db.reset_index(drop=True)
            db.drop("area",axis=1,inplace=True)
            print(end=timerstring()+" removed areas<%.2f, "%arealimit)
            print(len(db),"remaining polygons")
            if(count_points):
                pointscount = db["geometry"].apply(get_pointlenght).sum()
                print(pointscount,"points")
            timer()
            
            """Close holes"""
            def close_holes(poly: Polygon) -> Polygon:          
                #https://stackoverflow.com/questions/61427797/filling-a-hole-in-a-multipolygon-with-shapely-netherlands-2-digit-postal-codes
                if poly.interiors:
                    return Polygon(list(poly.exterior.coords))
                else:
                    return poly
            db["geometry"] = db["geometry"].apply(close_holes)
            print(timerstring()+" removed holes, %i poly"%len(db))
            if(count_points):
                pointscount = db["geometry"].apply(get_pointlenght).sum()
                print(pointscount,"points")
            timer()
            
            """Simplify geometry"""
            simplifylevel = 0.1
            db["geometry"]=db["geometry"].simplify(simplifylevel)
            print(timerstring()+" simplify %.2f"%simplifylevel)
            if(count_points):
                pointscount = db["geometry"].apply(get_pointlenght).sum()
                print(pointscount,"points")
            timer()
            
            """###Output to files###"""
            
            for column,value in database_names.keys():
                if(len(db[db[column]==value])>0):
                    group = database_names[(column,value)]
                    data=db[db[column]==value]
                    outputname = outpath+"/"+group+"_"+name
                    data.to_file(outputname)
                    print(timerstring(),"output",outputname)
                    del data
                    
                    # data2 = gpd.read_file(outputname)
                    # del data2
                    # print(timerstring(),"loaded saved data")
            del db

print("-"*4,timestamp(),"-"*4)
print(timerstring(1),"all done")