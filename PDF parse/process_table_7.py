import csv
import glob

def row_size(row):
    size=0
    for element in row:
        if(len(element.strip())>0):
            size+=1
    return size
        

for name in glob.glob("*.csv"):
    if("Table_7" in name and "(processed)" not in name):
        table_started=False
        print(name)
        year=int(name[:4])
        output_table=open(name.replace(".csv","(processed).csv"),"w",newline="")
        output_writer=csv.writer(output_table)
        with open(name, newline="") as csvfile:
            reader = csv.reader(csvfile)
            current_class="Unspecified"
            reason = ""
            for row in reader:
                if(year in (2012,2013,2014)):
                    row.pop(0)
                print(row_size(row))
                if(table_started==False and row_size(row)<=2):
                    continue
                else:
                    if(row_size(row)>2 and row[0]=="Scientific name" and table_started==False):
                        if(year==2008):
                            outputrow = row+["Reason","Class","Year"]
                        else:
                            outputrow = row+["Class","Year"]
                        output_writer.writerow(outputrow)
                        table_started=True
                    else:
                        if(row_size(row)==1):
                            if("Genuine" in row[0]):
                                reason = row[0]
                            else:
                                current_class=row[0]
                                print("Class change:",current_class)
                        elif(row_size(row)>2 and row[0]!="Scientific name"):
                            if(year==2008):
                                outputrow = row+[reason,current_class,year]
                            else:
                                outputrow = row+[current_class,year]
                            output_writer.writerow(outputrow)
                            print(outputrow)
          