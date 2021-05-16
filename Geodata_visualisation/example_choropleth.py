from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("fips-unemp-16.csv",
                   dtype={"fips": str})

import plotly.express as px

fig = px.choropleth_mapbox(df, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
import plotly.graph_objects as go
fig.add_trace(
    px.scatterplot(y=[90,90,-90,-90],x=[180,-180,180,-180])

)


coordinates = [[-200, 100],
               [200, 100],
               [200, -100],
               [-200, -100]]
from PIL import Image
# img = Image.open('RASTERISED_DATA/alpha300dpi_cropped/MAMMALS.shp_(3)VU_300DPI.png')
# img = Image.open('allmammals.png')
img = Image.open('RASTERISED_DATA/red100/alpha100DPIMARINEFISH_PART1.shp_(1)LC.png')
fig.update_layout(
    mapbox_layers = [
    {
        "sourcetype": "image",
        "source": img,
        "coordinates":coordinates
        }]
)

fig.update_geos(
    projection={"type": 'conic equidistant'}
    )
fig.show()