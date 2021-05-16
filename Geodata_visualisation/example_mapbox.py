import pandas as pd
df = pd.read_csv('REPTILES_points.csv')

"""
import datashader as ds
cvs = ds.Canvas(plot_width=1000, plot_height=1000)
agg = cvs.points(dff, x='Lon', y='Lat')
# agg is an xarray object, see http://xarray.pydata.org/en/stable/ for more details
coords_lat, coords_lon = agg.coords['Lat'].values, agg.coords['Lon'].values"""
# Corners of the image, which need to be passed to mapbox
"""coordinates = [[coords_lon[0], coords_lat[0]],
               [coords_lon[-1], coords_lat[0]],
               [coords_lon[-1], coords_lat[-1]],
               [coords_lon[0], coords_lat[-1]]]"""
coordinates = [[-180, 89],
               [180, 89],
               [180, -89],
               [-180, -89]]
print(coordinates)
from PIL import Image
#img=Image.open('allmammals.png')
img=Image.open('RASTERISED_DATA/alpha300dpi_cropped/MAMMALS.shp_(3)VU_300DPI.png')
img=Image.open('RASTERISED_DATA/red100/alpha100DPIMARINEFISH_PART1.shp_(1)LC.png')
import plotly.express as px
# Trick to create rapidly a figure with mapbox axes
fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', zoom=1)

fig.update_geos(projection_type="albers usa")
# Add the datashader image as a mapbox layer image
fig.update_layout(mapbox_style="carto-darkmatter",
                 mapbox_layers = [
                {
                    "sourcetype": "image",
                    "source": img,
                    "coordinates": coordinates
                }]
)
fig.show()