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
    'background': '#F8F8F8',
    'text': '#011020'
}
#load_data
def load_all_data():
    path="SIMPLIFIED_DATA"
    has_data = False
    alldata = None
    counter = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if name.endswith(("BIRCHES.shp")): #BIRCHES BONEFISH_TARPONS MAMMALS
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



categories=['DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', "EX"]
cat_colors=[(212,212,212),(100,100,100),(70,3,89),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]
color_of_cat = {cat:cat_colors[id] for (id,cat) in enumerate(categories)}
cat_names = ["Data defficient","Least concern","Near threatened", "Vulnerable", "Endangered", "Cricitally Endangered", "Extinct in the wild", "Extinct"]
class_names = list()
for dirpath, dirnames, filenames in os.walk("SIMPLIFIED_DATA"):
    for name in filenames:
        if name.endswith((".shp")):
            class_names.append(name[:-4])
print(len(class_names),class_names)
image_filenames = dict()
images_path = "RASTERISED_DATA/alpha300dpi_cropped/"
for dirpath, dirnames, filenames in os.walk(images_path):
    for name in filenames:
        for cat in categories:
            if ")"+cat+"_" in name:
                for classe in class_names:
                    if classe in name:
                        image_filenames[(cat,classe)]=images_path+name

"""fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)"""
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
point_coords = (70,70)
point = gpd.GeoSeries(Point([point_coords]))
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


multiselect_options = [{"label":classe,"value":classe} for classe in class_names]
multiselect_values = class_names[:]

#checklist_options  = [{"label":html.Mark(children=cat_names[i],id=cat),"value":cat} for i,cat in enumerate(categories)]
checklist_options  = [{"label":cat_names[i],"value":cat} for i,cat in enumerate(categories)]
checklist_values = categories[:]

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
    html.H1(children="Worldwide Animal Extinction Status",
        style={"textAlign":"center","color":colors["text"]}
        ),
    html.Div(children="Animal extinction status across the world. Click on the map"),
    
    html.Div(children=str(len(intersection))+" animals at [%s;%s]"%(point_coords)),
    generate_table(intersection),
    html.Label('Select the databases to search in'),
    dcc.Dropdown(
        options=multiselect_options,
        value=multiselect_values,
        multi=True
    ),
    html.Label('Select the extinction level categories to search in'),
    dcc.Checklist(
        options=checklist_options,
        value=checklist_values,
        id="extinction_category"
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)