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
output_table=open("Table_7_merge(processed).csv","w",newline="",encoding="utf-8-sig")
output_writer=csv.writer(output_table)
for name in glob.glob("*.csv"):
    if(("Table_7" in name or "Table7" in name) and "(processed)" not in name):
        print(name)
        year=int(name[:4])
        with open(name, newline="") as csvfile:
            reader = csv.reader(csvfile)
            current_class="Unspecified"
            reason = ""
            for row in reader:
                if(year in (2012,2013,2014)):
                    row.pop(0)
                #print(row_size(row))
                if(table_started==False and row_size(row)<=2):
                    continue
                else:
                    if(row_size(row)>2 and row[0]=="Scientific name" and table_started==False):
                        if(year==2008):
                            outputrow = row+["Reason for change","Red List version","Class","Table Year"]
                        else:
                            outputrow = row+["Class","Table Year"]
                        output_writer.writerow(outputrow)
                        #print(outputrow)
                        table_started=True
                    else:
                        if(row_size(row)==1):
                            if("Genuine" in row[0]):
                                reason = "G" #row[0]
                            else:
                                current_class=row[0]
                                #print("Class change:",current_class)
                        elif(row_size(row)>2 and row[0]!="Scientific name"):
                            if(year==2008):
                                outputrow = row+[reason,year,current_class,year]
                            else:
                                outputrow = row+[current_class,year]
                            output_writer.writerow(outputrow)
                            #print(outputrow)
output_table.close()
print("end")