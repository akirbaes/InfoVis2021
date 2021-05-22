
# This is the code were we add country code to table 6 for the vsualisation using py country
# code reference:   
# https://pypi.org/project/pycountry/

import pandas as pd
import matplotlib.pyplot as plt
import pycountry  # generate country code  based on country name 
import os
import numpy as np

Tab6=pd.read_csv('D:/DAMA_Notes/Semester2/IV/project/InfoVis2021/Table6_processed/redlist/processedTable/Table_6_merge(processed).csv')

def alpha3code(column):
    CODE=[]
    for country in column:
        try:
            code=pycountry.countries.get(name=country).alpha_3
           # .alpha_3 means 3-letter country code 
            CODE.append(code)
        except:
            CODE.append('None')
    return CODE

# create a column for code 
Tab6['CODE']=alpha3code(Tab6.Name)

# save table
Tab6.to_csv('D:/DAMA_Notes/Semester2/IV/project/InfoVis2021/Table6_processed/redlist/processedTable/Tab6_CountryCode.csv');
