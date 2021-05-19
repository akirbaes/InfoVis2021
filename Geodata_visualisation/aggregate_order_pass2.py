import geopandas as gpd
import pandas as pd
import time
import os
from simpledbf import Dbf5
from datetime import datetime
import colorama
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
	
def timestamp():
    return datetime.now().strftime("%H:%M:%S")
    
laptime()
timer()

def load_all_data():
    path="REDLIST"
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".dbf")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                # print("[%i/%i]Open"%(counter,total_count),pathname)
                counter+=1
                # db = gpd.read_file(pathname)
                dbf = Dbf5(pathname)
                db = dbf.to_dataframe()
                db.drop(["presence","origin","seasonal","compiler","SHAPE_Leng","SHAPE_Area","compiler","id_no","yrcompiled","citation","subspecies","subpop","source", "island", "tax_comm", "dist_comm", "legend"],axis=1,inplace=True)
                #db["origin"]=pathname
                #print("Finished reading database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db,ignore_index=True)
                
                #print(timerstring(),"Merged databases")
                #print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata
    
dbdata = load_all_data()
print(len(dbdata),"animal database loaded")
print("-"*4,timestamp(),"-"*4)
    
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
    
path="ORDER_AGGREGATED_DATA"
has_data = False
agg_layers = None
total_count=0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")):
            total_count+=1
counter = 0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS  and counter<4
            counter+=1
            pathname =os.path.join(dirpath, name)
            db = gpd.read_file(pathname)
            print("[%i/%i]Open"%(counter,total_count),pathname)
            db["kingdom"]=name[0:find_nth(name,"_",1)]
            db["phylum"]=name[find_nth(name,"_",1)+1:find_nth(name,"_",2)]
            db["class"]=name[find_nth(name,"_",2)+1:find_nth(name,"_",3)]
            db["order_"]=name[find_nth(name,"_",3)+1:find_nth(name,"_",4)]
            db["type"]=name[find_nth(name,"_",4)+1:find_nth(name,"_",5)]
            if(has_data==False):
                has_data=True
                agg_layers=db
            else:
                agg_layers=agg_layers.append(db,ignore_index=True)
            print(lapstring(),"Finished reading database")
print("Loaded layers:")
print(agg_layers.head())
all_types = agg_layers["type"].unique()
all_orders = agg_layers["order_"].unique()

all_colors = agg_layers["color"].unique()
print("All existing colors:",all_colors)

def dissolve_all_colors(db):
    total = None
    for color in db["color"].unique():
        new = dissolve_color(db[db["color"]==color])
        try:total=total.append(new)
        except:total=new
    return total
def dissolve_color(order_aggregation):
    size = len(order_aggregation["color"].unique())
    # order_aggregation = order_aggregation.sort_values("color")
    # print("Recovering:")
    # print(order_aggregation)
    while(len(order_aggregation)>size):
        line = "%i>%s"%(len(order_aggregation),size)
        print(end="\033[%iD"%(len(line))+line)
        tmp = None
        
        for cnt in range(0,len(order_aggregation),2):
            # print("count",cnt,"/",len(order_aggregation))
            # print(order_aggregation.iloc[[cnt]])
            if(cnt<len(order_aggregation)-1):
                new=order_aggregation.iloc[[cnt,cnt+1]].dissolve(by="color", as_index=False)
                new["geometry"]=new.simplify(0.1)
            else:
                new=order_aggregation.iloc[[cnt]]
            # print(new)
            if(tmp is None):tmp=new
            else:tmp=tmp.append(new)
        order_aggregation=tmp
    return order_aggregation

palette=['DD', 'LC', 'LR/lc', 'NT', 'LR/cd', 'VU', 'EN', 'CR', 'EW', "EX"]
try:os.mkdir("ALL_AGGREGATE_LAYERS")
except:pass
try:os.mkdir("SEPARATE_AGGREGATE_LAYERS")
except:pass
pd.options.mode.chained_assignment=None
print("-"*4,timestamp(),"-"*4)
print("order")
has_data = False
all_order_aggregation = None
for ordid,order in enumerate(all_orders):
    print("--",order,ordid+1,"/",len(all_orders))
    for type in all_types:
        order_aggregation = agg_layers[(agg_layers["type"]==type) & (agg_layers["order_"]==order)]
        if(len(order_aggregation)==0):continue
        #ord = order_aggregation
        order_aggregation=dissolve_all_colors(order_aggregation)
        #order_aggregation=order_aggregation.dissolve(by="color", as_index=False)
        order_aggregation["identifier"]=order
        order_aggregation["id_type"]="order_"
        # print(order_aggregation.head())
        def get_count(color):
            #there seems to be a mismatch somewhere in the aggregated data
            #On category vs color index
            #print("*"*5+"Get",type,order,palette[int(color)],len(dbdata))
            #print(dbdata[(dbdata["order_"]==order)])
            selection = dbdata[(dbdata["order_"]==order) & (dbdata["category"]==palette[int(color)]) & (dbdata[str(type)]=="true")]
            #print(len(selection),"found")
            
            return len(selection)
        order_aggregation["count"]=order_aggregation["color"].apply(get_count)
        order_aggregation["geometry"]=order_aggregation.simplify(0.1)
        
        order_aggregation.to_file("SEPARATE_AGGREGATE_LAYERS/order_%s_%s.shp"%(order,type))
        if(has_data==False):
            has_data=True
            all_order_aggregation = order_aggregation
            # print("Created",len(all_order_aggregation),"from",len(order_aggregation))
        else:
            # print("Added",len(order_aggregation),"to",len(all_order_aggregation))
            all_order_aggregation=all_order_aggregation.append(order_aggregation,ignore_index=True)
            # print("Length:",len(all_order_aggregation))
print("Aggregated all orders (%i)"%len(all_order_aggregation))
all_order_aggregation.reset_index(drop=True, inplace=True)
print(all_order_aggregation.head())
all_order_aggregation.to_file("ALL_AGGREGATE_LAYERS/order.shp")

columns=["order_","class","phylum","kingdom"]
variables = [all_order_aggregation["class"].unique(), all_order_aggregation["phylum"].unique(), all_order_aggregation["kingdom"].unique()]
del agg_layers
aggregations = [all_order_aggregation]
for index in range(len(columns)-1):
    print("-"*4,timestamp(),"-"*4)
    column = columns[index+1]
    print(column)
    has_data = False
    all_aggregation = None
    for var in variables[index]:
        print("--",var)
        for type in all_types:
            prev_agg = aggregations[-1]
            aggregation = prev_agg[(prev_agg["type"]==type) & (prev_agg[column]==var)]
            if(len(aggregation)==0):continue
            
            # print(type,var,len(aggregation))
            # print(aggregation.head())
            # print("Drop",columns[index])
            aggregation.drop(str(columns[index]),axis=1,inplace=True) #drop previous aggregation column

            aggregation = dissolve_all_colors(aggregation)
            # size = len(aggregation["color"].unique())
            # while(len(aggregation)>size):
                # line = "%i>%s"%(len(order_aggregation),size)
                # print(end="\033[%iD"%(len(line))+line)
                # tmp = None
                # for cnt in range(0,len(aggregation),2):
                    # # print("count",cnt,"/",len(aggregation))
                    # # print(aggregation.iloc[[cnt]])
                    # if(cnt<len(aggregation)-1):
                        # new=aggregation.iloc[[cnt,cnt+1]].dissolve(by="color", as_index=False)
                        # new.loc["geometry"]=new.simplify(0.1)
                    # else:
                        # new=aggregation.iloc[[cnt]]
                    # # print(new)
                    # if(tmp is None):tmp=new
                    # else:tmp=tmp.append(new)
                # aggregation=tmp
            
            
            
            # aggregation = aggregation.dissolve(by="color", as_index=False)
            def get_count(color):
                selection = dbdata[(dbdata[column]==var) & (dbdata["category"]==palette[int(color)-1]) & (dbdata[str(type)]=="true")]
                return len(selection)
            aggregation["count"]=aggregation["color"].apply(get_count)
            aggregation["identifier"]=var
            aggregation["id_type"]=column
            aggregation.reset_index(drop=True, inplace=True)
            aggregation["geometry"]=aggregation.simplify(0.1)

            aggregation.to_file("SEPARATE_AGGREGATE_LAYERS/%s_%s_%s.shp"%(column,var,type))
            if(has_data==False):
                has_data=True
                all_aggregation = aggregation
            else:
                all_aggregation.append(aggregation,ignore_index=True)
    aggregations.append(all_aggregation)
    print("Aggregated all", column,"(%i)"%len(all_aggregation))
    print(all_aggregation.head())
    all_aggregation.to_file("ALL_AGGREGATE_LAYERS/%s.shp"%column)
    
if(0):
    # has_data = False
    # all_class_aggregation = None
    # for classe in all_classes:
        # for type in all_types:
            # class_aggregation = all_order_aggregation[(all_order_aggregation["type"]==type)
                    # & (all_order_aggregation["class"]==classe)]
            # if(len(class_aggregation)==0):continue
            # print(type,classe,len(class_aggregation))
            # print(class_aggregation.head())
            # class_aggregation.drop("order_",axis=1)
            # class_aggregation = class_aggregation.dissolve(by="color", as_index=False)
            # def get_count(color):
                # selection = dbdata[(dbdata["class"]==classe) & (dbdata["category"]==palette[int(color)-1]) & (dbdata[str(type)]=="true")]
                # return len(selection)
            # class_aggregation["count"]=class_aggregation["color"].apply(get_count)
            # class_aggregation["identifier"]=classe
            # class_aggregation["id_type"]="class"
            # class_aggregation.reset_index(drop=True, inplace=True)
            # class_aggregation["geometry"]=class_aggregation.simplify(0.1)

            # if(has_data==False):
                # has_data=True
                # all_class_aggregation = class_aggregation
            # else:
                # all_class_aggregation.append(class_aggregation,ignore_index=True)
    # print("Aggregated all class")
    # print(all_class_aggregation.head())
    # all_class_aggregation.to_file("ALL_AGGREGATE_LAYERS/class.shp")

    # has_data = False
    # all_phylum_aggregation = None
    # for phylum in all_phylums:
        # for type in all_types:
            # phylum_aggregation = all_class_aggregation[(all_class_aggregation["type"]==type)
                    # & (all_class_aggregation["phylum"]==phylum)]
            # if(len(phylum_aggregation)==0):continue
            # phylum_aggregation.drop("class",axis=1)
            # phylum_aggregation = phylum_aggregation.dissolve(by="color", as_index=False)
            # def get_count(color):
                # selection = dbdata[(dbdata["phylum"]==phylum) & (dbdata["category"]==palette[int(color)-1]) & (dbdata[str(type)]=="true")]
                # return len(selection)
            # phylum_aggregation["count"]=phylum_aggregation["color"].apply(get_count)
            # phylum_aggregation["identifier"]=phylum
            # phylum_aggregation["id_type"]="phylum"
            # phylum_aggregation.reset_index(drop=True, inplace=True)
            # phylum_aggregation["geometry"]=phylum_aggregation.simplify(0.1)
            
            # if(has_data==False):
                # has_data=True
                # all_phylum_aggregation = phylum_aggregation
            # else:
                # all_phylum_aggregation.append(phylum_aggregation,ignore_index=True)
    # print("Aggregated all phylum")
    # print(all_phylum_aggregation.head())
    # all_phylum_aggregation.to_file("ALL_AGGREGATE_LAYERS/phylum.shp")
            
    # has_data = False
    # all_kingdom_aggregation = None
    # for kingdom in all_kingdoms:
        # for type in all_types:
            # kingdom_aggregation = all_phylum_aggregation[(all_phylum_aggregation["type"]==type)
                    # & (all_phylum_aggregation["kingdom"]==kingdom)]
            # if(len(kingdom_aggregation)==0):continue
            # kingdom_aggregation.drop("phylum",axis=1)
            # kingdom_aggregation = kingdom_aggregation.dissolve(by="color", as_index=False)
            # def get_count(color):
                # selection = dbdata[(dbdata["kingdom"]==kingdom) & (dbdata["category"]==palette[int(color)-1]) & (dbdata[str(type)]=="true")]
                # return len(selection)
            # kingdom_aggregation["count"]=kingdom_aggregation["color"].apply(get_count)
            # kingdom_aggregation["identifier"]=kingdom
            # kingdom_aggregation["id_type"]="kingdom"
            # kingdom_aggregation.reset_index(drop=True, inplace=True)
            # kingdom_aggregation["geometry"]=kingdom_aggregation.simplify(0.1)
            
            # if(has_data==False):
                # has_data=True
                # all_kingdom_aggregation = kingdom_aggregation
            # else:
                # all_kingdom_aggregation.append(kingdom_aggregation,ignore_index=True)
    # print("Aggregated all kingdom")
    # print(all_kingdom_aggregation.head())
    # all_kingdom_aggregation.to_file("ALL_AGGREGATE_LAYERS/kingdom.shp")
    pass

print("-"*4,timestamp(),"-"*4)
has_data = False
all_global_aggregation = None
for type in all_types:
    prev_agg=aggregations[-1]
    global_aggregation = prev_agg[prev_agg["type"]==type]
    global_aggregation = global_aggregation.drop("kingdom",axis=1).dissolve(by="color", as_index=False)
    def get_count(color):
        selection = dbdata[(dbdata["category"]==palette[int(color)-1]) & (dbdata[str(type)]=="true")]
        return len(selection)
    global_aggregation["count"]=global_aggregation["color"].apply(get_count)
    global_aggregation["color"]=global_aggregation.index
    global_aggregation["id_type"]="global"
    global_aggregation["identifier"]="global"
    global_aggregation["geometry"]=global_aggregation.simplify(0.1)
    if(len(global_aggregation)==0):
        continue
    global_aggregation.to_file("SEPARATE_AGGREGATE_LAYERS/global_%s.shp"%(type))
    if(has_data==False):
        has_data=True
        all_global_aggregation = global_aggregation
    else:
        all_global_aggregation=all_global_aggregation.append(global_aggregation,ignore_index=True)
print("Aggregated all (global) (%i)"%len(all_global_aggregation))
print(all_global_aggregation.head())
all_global_aggregation.to_file("ALL_AGGREGATE_LAYERS/global.shp")

all_aggregations = aggregations

for index,agg in enumerate(all_aggregations):
    columns=["order_","class","phylum","kingdom"][index:]
    # print("Drop",columns,"from")
    # print(agg.head())
    all_global_aggregation=all_global_aggregation.append(agg.drop(columns,axis=1),ignore_index=True)
print("Merged all (%i)"%len(all_global_aggregation))
print(all_global_aggregation)


try:os.mkdir("ALL_AGGREGATE_LAYERS_MERGED")
except:pass
all_global_aggregation.to_file("ALL_AGGREGATE_LAYERS_MERGED/merged_aggregation.shp")

print("-"*4,timestamp(),"-"*4)
print(timerstring(),"Aggregating all files done")
print("Done")