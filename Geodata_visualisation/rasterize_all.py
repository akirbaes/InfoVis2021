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
from datetime import datetime
import os
start_time = time.time()
last_time = time.time()
entire_time = time.time()

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
def rasterize_database(filename,outputname):
    print("-"*4,timestamp(),"-"*4)
    print("Reading",filename)
    timer()
    laptime()
    database = gpd.read_file(filename)
    print(timerstring()+"Finished reading database")
    palette=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
    colors=[(212,212,212),(100,100,100),(70,3,89),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
    names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
    colordict = dict()
    for i,p in enumerate(palette):
        c=[x/256 for x in colors[i]]
        colordict[p]=c
    
    for entry in palette:
        db=database[database["category"]==entry]
        if len(db)>0:
            print("Output for",entry,":",len(db),"shapes")
            timer()
            color=colordict[entry]
            fig=plt.figure()
            ax=fig.add_subplot(111)
            gplt.polyplot(db,alpha=0.3,facecolor=color,edgecolor=None,linewidth=0,extent=(-180, -90, 180, 90),ax=ax)
            print(timerstring(),"Plot time")
            plt.tight_layout()
            ax.autoscale_view('tight')
            dp=100
            x = [-180]#,-180,180,180]
            y = [90]#,90,-90,90]
            plt.scatter(x=x,y=y, marker=',', color='red', linewidths=0,s=0.75,zorder=10)
            x = [180]
            y = [-90]
            plt.scatter(x=x,y=y, marker=',', color='green', linewidths=0,s=0.75,zorder=10)
            imagename = "alpha"+str(dp)+"DPI"+outputname+"_("+str(palette.index(entry))+")"+entry+".png"
            foldername = "RASTERISED_DATA/red%i/"%dp
            try: os.mkdir(foldername)
            except:pass
            plt.savefig(foldername+imagename,dpi=dp,transparent=True)
            print(timerstring(),"Saved",imagename)
            plt.clf()
            
            """
            timer()
            color=colordict[entry]
            fig=plt.figure()
            ax=fig.add_subplot(111)
            gplt.polyplot(db,alpha=1,facecolor=color,edgecolor=None,linewidth=0,extent=(-180, -90, 180, 90),ax=ax)
            print(timerstring(),"Solid plot time")
            plt.tight_layout()
            ax.autoscale_view('tight')
            dp=600
            imagename = "solid"+str(dp)+"DPI"+outputname+"_("+str(palette.index(entry))+")"+entry+".png"
            plt.savefig("RASTERISED_DATA/solid600/"+imagename,dpi=dp,transparent=True)
            print(timerstring(),"Saved",imagename)
            plt.clf()"""

    print("Total duration: %ss"%(laptime()))
    
    
	
path="REDLIST"
has_data = False
alldata = None
counter = 0
for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
        if name.endswith((".shp")): #BIRCHES BONEFISH_TARPONS
            print("--"*4,counter,"--"*4)
            pathname =os.path.join(dirpath, name)
            rasterize_database(pathname,name)
            counter+=1
print("*"*4,timestamp(),"*"*4)
print("Done in",entire_time-time.time(),'seconds')