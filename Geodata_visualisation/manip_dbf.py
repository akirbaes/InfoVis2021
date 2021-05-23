import pandas as pd
import geopandas as gpd
import os
from simpledbf import Dbf5



def load_all_data():
    path="REDLIST"
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith((".dbf")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                print("Open",str(counter),pathname)
                counter+=1
                # db = gpd.read_file(pathname)
                dbf = Dbf5(pathname)
                db = dbf.to_dataframe()
                db["origin"]=pathname
                #print("Finished reading database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db)
                
                #print(timerstring(),"Merged databases")
                #print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata
#data is in alldata

alldata = load_all_data()
print(alldata.head())

genegraph = dict()


class_show = alldata[["kingdom","phylum","class","binomial"]]
class_show["counter"]=1
class_show=class_show.groupby(["kingdom","phylum","class"]).sum()
print(class_show)

# phylums = alldata[["kingdom","phylum","class"]].drop_duplicates()
classified = alldata[["kingdom","phylum","class","order_","origin"]]
# phylums = alldata[["kingdom","phylum","class","order_"]]
classified["counter"]=1
# phylums.duplicated()
#phylums["dupes"]=phylums["dupes"].sum()
classified=classified.groupby(["kingdom","phylum","class","order_","origin"]).sum()
# phylums=phylums.groupby(["kingdom","phylum","class","order_"]).sum()
pd.set_option('display.max_rows', None)
print(classified)

#print(classified.to_dict())


kingdoms = alldata["kingdom"].unique()
print(kingdoms)
for k in kingdoms:
    genegraph[k] = dict()
    phylums = classified[classified["kingdom"]==k]["phylum"].unique()
    for p in phylums:
        genegraph[k][p]=dict()
        classes = classified[classified["phylum"]==p]["class"].unique()
        for c in classes:
            genegraph[k][p][c]=dict()
            orders_ = classified[classified["class"]==c]["order_"].unique()
            for o in orders_:
                genegraph[k][p][c][o]=dict()
                filenames = classified[classified["order_"]==o]["origin"].unique()
                for filename in filenames:
                    selection = classified[(classified["order_"]==o) & (classified["origin"]==filename)]["counter"]
                    #print(filename,selection)
                    genegraph[k][p][c][o][filename] = int(selection.iat[0])
                    
print(genegraph)

import pickle

with open("database_structure.pickle","wb") as f:
    pickle.dump(genegraph,f)