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
output_table=open("Table_8_merge(processed).csv","w",newline="",encoding="utf-8-sig")
output_writer=csv.writer(output_table)
output_titles = ("Group","Specie","Total endemics","Threatened endemics","Country","Region")
output_writer.writerow(output_titles)
for name in glob.glob("*Table8*.csv"):
    print(name)
    year=int(name[:4])
    if("Table8a" in name):
        group = "Vertebrate"
    elif("Table8b" in name):
        group = "Invertebrate"
    elif("Table8c" in name):
        group = "Plant"
    
    with open(name, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row_size(row)==1:
                current_region = row[0]
            elif(row[0]==""):
                if('Total\rendemics' in row or row_size(row)==0):
                    pass
                else:
                    current_species = [specie.replace("\n"," ").replace("\r"," ") for specie in row if len(specie)>1]
                    print(current_species)
                    """for spec in current_species:
                        if("\n" in spec):
                            print(spec)"""
            else:
                country=row[0]
                data = [int(elem) for elem in row[1:] if elem!=""]
                print(data)
                for index in range(0,len(data),2):
                    specie = current_species[index//2]
                    total_endemics=data[index]
                    threatened_endemics=data[index+1]
                    if(total_endemics>0):
                        datapoint = [group,specie,total_endemics,threatened_endemics,country,current_region]
                        output_writer.writerow(datapoint)
output_table.close()
print("end")