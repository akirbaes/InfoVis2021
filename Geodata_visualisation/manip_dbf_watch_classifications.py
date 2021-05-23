import pandas as pd
import geopandas as gpd
import os
from simpledbf import Dbf5




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
# print(" & ".join(("Dataset","Kingdoms","Phylums","Classes","Orders","Groupings", "Unnacounted"))+"\\\\")
gps = list(g for g in database_names.values())
groupings = list(g[:3]for g in database_names.values())
print(" & ".join(["Dataset"]+groupings+["Other"])+"\\\\")
print("\\hline")
total_accounting = [0]*len(gps)
total_unnacounted = 0
collect = dict()
for name in gps:
    collect[name]=0

path="REDLIST"
has_data = False
alldata = None
counter = 0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".dbf")): #BIRCHES BONEFISH_TARPONS MAMMALS
            pathname =os.path.join(dirpath, name)
            #print("Open",str(counter),pathname)
            counter+=1
            # db = gpd.read_file(pathname)
            dbf = Dbf5(pathname)
            db = dbf.to_dataframe()
            db["origin"]=pathname
            counting = []
            accounting = [" "]*len(gps)
            total_count = 0
            for mode in ("kingdom","phylum","class","order_"):
                counting.append(str(len(db[mode].unique())))
            for mode,value in database_names:
                gname = database_names[(mode,value)]
                count = len(db[db[mode]==value])
                if(count>0):
                    accounting[gps.index(gname)]=count
                    total_count+=count
                    total_accounting[gps.index(gname)]+=count
                
            accounting=[str(i) for i in accounting]
            unnacounted = len(db)-total_count
            total_unnacounted+=unnacounted
            # print(" & ".join([name[:-4]]+counting+[accounting]+[str(unnacounted)])+" \\\\")
            print(" & ".join([name[:-4]]+accounting+[str(unnacounted)])+" \\\\")
            print("\\hline")
            #print("Finished reading database")
            
            #print(timerstring(),"Merged databases")
            #print("Elements:",alldata.size,"Shape:",alldata.shape)

print(" & ".join(["Total"]+[str(i) for i in total_accounting]+[str(total_unnacounted)])+" \\\\")



for i in range(len(database_names)):
    column, value = list(database_names.keys())[i]
    groupname = gps[i]
    count = total_accounting[i]
    print(" & ".join(str(j) for j in [column, value,groupname,count])+"\\\\")
    print("\\hline")
