#!python2
#coding:utf8
import csv
import glob

def row_size(row):
    size=0
    for element in row:
        if(len(element.strip())>0):
            size+=1
    return size
        

table_started=False
output_table=open("2020-3_RL_Stats_Table1b(processed).csv","w",newline="",encoding="utf-8-sig")
output_writer=csv.writer(output_table)
input_table=open("2020-3_RL_Stats_Table1b(some_cleaning).csv",newline="")
reader = csv.reader(input_table)

output_titles = ("Year","Version","Kingdom","Class","Total assessed","Total threatened")
output_writer.writerow(output_titles)


global partial_lines
partial_lines = None
for row_index,row in enumerate(reader):
    if(row_size(row)>2):
        #contains kingdom and for animals, phylum (vertebrate or invertebrate)
        if "VERTEBRATES" in row:
            col_kingdom = list()
            for j, entry in enumerate(row):
                if(len(entry)>1):
                    col_kingdom.append((j,entry))
            col_kingdom.reverse()
            global column_kingdom
            def column_kingdom(column):
                for start,kingdom in col_kingdom:
                    if column>=start:
                        return kingdom
        #contains classes for each kingdom
        elif "Mammals" in row:
            global column_titles
            column_titles = [x.replace("\n"," ") for x in row]
            """col_classes = list()
            for j, entry in enumerate(row):
                if(len(entry)>1):
                    col_classes.append((j,entry))
            global column_class
            def column_class(column):
                for start,clas in col_classes.reverse():
                    if column>=start:
                        return clas"""
        #double line with number of species started
        elif len(row[0])>1 and ("Year" not in row[0]):
            partial_lines = dict()
            version_data=row[0]
            year=int(str(version_data)[:4])
            if(len(str(version_data))==4 or ("/" in version_data)):
                version = 0
            else:
                version=int(version_data[-2])
            
            #2 to skip the year and "total assessed" cases
            for column_index in range(2,len(row)):
                clas=column_titles[column_index]
                #animal classes
                if(len(clas)>1 and "Subtotal" not in clas):
                    kingdom = column_kingdom(column_index)
                    
                    assessed=row[column_index]
                    partial_lines[clas]=[year,version,kingdom,clas,assessed]
        #second part of the double line
        elif partial_lines:
            #2 to skip the year and "total assessed" cases
            for column_index in range(2,len(row)):
                clas=column_titles[column_index]
                #animal classes
                if(len(clas)>1 and "Subtotal" not in clas):
                    threatened=row[column_index]
                    output_line=partial_lines[clas]+[threatened]
                    output_writer.writerow(output_line)
            partial_lines=None

output_table.close()
print("end")