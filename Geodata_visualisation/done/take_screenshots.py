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

start_time = time.time()

database = gpd.read_file("REDLIST/MAMMALS/MAMMALS.shp")
#database = gpd.read_file("AGGREGATED_DATA/_agg_MAMMALS.shp")
# filler = gpd.read_file("AGGREGATED_DATA/_agg_MAMMALS.shp")
#filler = filler["category"]=="LC"
#filler.reset_index()
#print(filler.head())
#filler=gpd.GeoDataFrame(filler, geometry=filler["geometry"])
# database = gpd.read_file("REDLIST/MAMMALS/MAMMALS.shp")
# database = gpd.read_file("SIMPLIFIED_DATA/MAMMALS.shp")
#database = gpd.read_file("REDLIST/MAMMALS_FRESHWATER/MAMMALS_FRESHWATER.shp")
#database = gpd.read_file("REDLIST/REPTILES_points/REPTILES_points.csv")

print("Finished reading database at %s seconds"%(time.time()-start_time))

start_time = time.time()

palette=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]

colors=[(212,212,212),(128,128,128),(70,3,89),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
colordict = dict()
for i,p in enumerate(palette):
    c=[x/256 for x in colors[i]]
    colordict[p]=c
def get_color(cat):
    return palette.index(cat)

database["color"]=database["category"].apply(get_color)
print(database.color.head())
categories = database["category"].unique()
print(categories)
print(len(categories))

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

#database["color"]=7

#database.plot();
#category = database['category']
#scheme = mapclassify.Quantiles(category, k=5)

#print(database["category"].unique())
#database=database["binomial"]=="Vulpes lagopus"
#selection=database["category"]=="DD"
#database.where(selection, inplace=True)
    
#plt.rcParams['savefig.facecolor'] = "0.8"
#plt.tight_layout(True)
#fig=plt.figure()
#fig.frameonbool=True
database.sort_values(by="color",axis=0,ascending=True,inplace=True)
for entry in palette:
    db=database[database["category"]==entry]
    print(len(db))
    if len(db)>0:
        color=colordict[entry]
        #scheme=mc.EqualInterval(database["color"],k=len(palette))
        #ax=db.plot(color='#000000', style_kwds={"alpha":0.3})
        #gplt.choropleth(db,alpha=0.3,hue=database["color"],color="black",edgecolor=None,fill=True)
        #gplt.polyplot(db,kwargs={"alpha":0.3,"facecolor":(0,0,0),"edgecolor":None,"fill":True})
        #ax=gplt.polyplot(filler,alpha=1,facecolor="red",edgecolor=None,linewidth=0)
        #ax.use_sticky_edges = False
        #ax.margins(2, 2)
        fig=plt.figure()
        #fig.patch.set_facecolor('blue')
        ax=fig.add_subplot(111)
        gplt.polyplot(db,alpha=0.3,facecolor=color,edgecolor=None,linewidth=0,extent=(-180, -90, 180, 90),ax=ax)
        plt.tight_layout()
        
        #plt.axis('tight')
        ax.autoscale_view('tight')
        
        #ax.autoscale_view('tight')
        #mng = plt.get_current_fig_manager()
        #mng.full_screen_toggle()
        #mng.frame.Maximize(True)
        dp=300
        print("DPI",dp,"__output_"+str(palette.index(entry))+entry+".png")
        plt.savefig("RASTERISED_DATA/"+"__output_"+str(palette.index(entry))+entry+".png",dpi=dp,transparent=True)
        # figManager = plt.get_current_fig_manager()
        # figManager.window.showMaximized()
        #plt.show()
        plt.clf()
        #ax.imshow(ruh_m, zorder=0, extent = BBox, aspect= 'equal')
        #plt.savefig("RASTERISED_DATA/Output_"+entry+".png",transparent=True)

#plt.savefig("RASTERISED_DATA/"+"GLOBALOUTPUT.png",dpi=dp,transparent=True)
"""leg=ax1.get_legend()
for i,e in enumerate(palette):
    leg.get_texts()[i].set_text(names[i])"""
#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
#world.plot();

#gplt.polyplot(database)
#gplt.polyplot(world)
#plt.show()
print("Finished showing the database at %s seconds"%(time.time()-start_time))