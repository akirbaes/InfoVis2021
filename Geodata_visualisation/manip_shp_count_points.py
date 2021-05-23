import pandas as pd
import geopandas as gpd
import os
import time
from datetime import datetime

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

g_interior_shapes, g_exterior_shapes, g_interior_points, g_exterior_points = 0,0,0,0

def count_shapes(db):
    interior_shapes = 0
    exterior_shapes = 0
    interior_points = 0
    exterior_points = 0
    for shape in db["geometry"]:
        if(shape.geom_type == 'MultiPolygon'):
            iter = shape
        elif(shape.geom_type == 'Polygon'):
            iter=[shape]
        else:
            print(shape.geom_type)
        exterior_shapes+=len(iter)
        for poly in iter:
            exterior_points += len(poly.exterior.coords)
            interior_shapes+=len(poly.interiors)
            for interior in poly.interiors:
                interior_points += len(interior.coords)
        
    global g_interior_shapes, g_exterior_shapes, g_interior_points, g_exterior_points
    g_interior_shapes += interior_shapes
    g_exterior_shapes += exterior_shapes
    g_interior_points += interior_points
    g_exterior_points += exterior_points
    return exterior_shapes, exterior_points, interior_shapes, interior_points 

print("Name & Loading & Entries & Exterior & Points & Interior & Points & Total shapes \\\\")
print("\\hline")
total_timer = 0
def load_all_data():
    path="REDLIST"
    has_data = False
    alldata = 0
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".dbf")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                timer()
                timer(1)
                #print(name[:-4].replace("_","\\_")+", ")
                counter+=1
                db = gpd.read_file(pathname)
                timersave = timerstring()
                global total_timer
                total_timer+=timer(1)
                exterior_shapes, exterior_points, interior_shapes, interior_points = count_shapes(db)
                total = sum((exterior_shapes, exterior_points, interior_shapes, interior_points ))
                print(name,"&",timersave,"&",len(db),"& %i & %i & %i & %i & %i \\\\"%(exterior_shapes, exterior_points, interior_shapes, interior_points, total))
                alldata+=len(db)
                print("\\hline")
                #dbf = Dbf5(pathname)
                #db = dbf.to_dataframe()
                db["origin"]=name
                #print("Finished reading database")
                # if(has_data==False):
                    # has_data=True
                    # alldata=db
                # else:
                    # alldata=alldata.append(db)
                del db
                
                #print(timerstring(),"Merged databases")
                #print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata
#data is in alldata
timer()
alldata = load_all_data()
print(timerstring(2),"loaded all data")
totall = sum((g_exterior_shapes, g_exterior_points, g_interior_shapes, g_interior_points))
print("Total & ",str(int(total_timer)),"&",alldata,"& %i & %i & %i & %i & %i"%(g_exterior_shapes, g_exterior_points, g_interior_shapes, g_interior_points, totall))


print("total interior_shapes poly:",  g_interior_shapes)
print("total exterior_shapes poly:",  g_exterior_shapes)
print("total interior_points",        g_interior_points)
print("total exterior_points",        g_exterior_points)

print()

print(alldata)
print(len(alldata), len(alldata["SHAPE_Leng"]),len(alldata["binomial"].unique()))