import pandas as pd
import plotly.express as px
import geopandas as gpd
import pyproj
#based on https://stackoverflow.com/questions/65507374/plotting-a-geopandas-dataframe-using-plotly
# reading in the shapefile
fp = "./data/"
fp = "AGGREGATED_DATA/_agg_MAMMALS.shp"
map_df = gpd.read_file(fp)
map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

merged = map_df
#df = pd.read_csv("./data/loans_amount.csv")
# join the geodataframe with the cleaned up csv dataframe
#merged = map_df.set_index('District').join(df.set_index('District'))
#merged = merged.reset_index()
merged.head()

fig = px.choropleth_mapbox(merged, geojson=merged.geometry, locations=merged.index, color="color", 
                           mapbox_style="carto-positron")
#fig.update_geos(fitbounds="locations")
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig.show()