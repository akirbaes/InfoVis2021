import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import geopandas as gpd
import os
import time
from shapely.geometry import Point, Polygon

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
	
laptime()


external_stylesheets = ["https://codepen.iochriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
colors = {
    'background': '#118811',
    'text': '#7FDBFF'
}
#load_data
def load_all_data():
    path="SIMPLIFIED_DATA"
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith(("MAMMALS.shp")): #BIRCHES BONEFISH_TARPONS MAMMALS
                pathname =os.path.join(dirpath, name)
                print("Open",str(counter),pathname)
                counter+=1
                db = gpd.read_file(pathname)
                print(timerstring(),"Finished reading database")
                if(has_data==False):
                    has_data=True
                    alldata=db
                else:
                    alldata=alldata.append(db)
                
                #print(timerstring(),"Merged databases")
                print("Elements:",alldata.size,"Shape:",alldata.shape)
    return alldata
#data is in alldata

alldata = load_all_data()


df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns[:-2]])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns[:-2] 
                ])for i in range(min(len(dataframe),max_rows))
            ])
        ])

print(alldata.head(10))
print(alldata.columns)

print("My crs:",alldata.crs)

# point = gpd.GeoSeries(Polygon([(-160,-90),(-160,90),(160,90),(160,-90)]))
point = gpd.GeoSeries(Point([(70,70)]))
point.set_crs(epsg=4326,inplace=True)
print("Point's crs:",point.crs)
#point=point.to_crs("EPSG:4326")
#point = point.to_crs(alldata.crs)
point=gpd.GeoDataFrame(geometry=point)
#alldata = alldata.to_crs(point.crs)
#intersection = alldata.intersects(point)
intersection = gpd.sjoin(alldata, point, op='intersects')
#dataframe = alldata.loc[intersection]

print(intersection.head(20))
print("Intersection:",len(intersection))
#print(dataframe.head(10))

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
    html.H1(children="Worldwide Animal Extinction Status",
        style={"textAlign":"center","color":colors["text"]}
        ),
    html.Div(children="Animal extinction status across the world. Click on the map"),
    
    dcc.Graph(id="example-graph",
    figure=fig
    ),
    generate_table(intersection)
])

if __name__ == "__main__":
    app.run_server(debug=True)