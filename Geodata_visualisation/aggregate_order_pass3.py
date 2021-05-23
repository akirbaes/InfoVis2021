import pickle
with open("./database_structure.pickle","rb") as f:
    genegraph = pickle.load(f)
	
import geopandas as gpd
import pandas as pd