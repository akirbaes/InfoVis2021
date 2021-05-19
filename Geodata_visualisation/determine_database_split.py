import pickle
with open("./database_structure.pickle","rb") as f:
    genegraph = pickle.load(f)

def sum_down(d):
    #print(d)
    if isinstance(d,int):
        return d
    else:
        return sum((sum_down(d[k]) for k in d.keys()))
        
def sum_files(d,parentage = []):
    #print(d)
    if isinstance(d,int):
        return [parentage[-1]]
    else:
        preset = (sum_files(d[k],parentage+[k]) for k in d.keys())
        return set_collapse(preset)
def set_collapse(preset):
    return set(a for l in preset for a in l)
    
#print(genegraph)
        
#print("Total sum:",sum_down(genegraph))
def collapse_sum(d):
    k = list(d.keys())
    if(k[0].startswith("RED")):
        print(k[0])
        return sum_down(d)
    else:
        for e in k:
            d[e]=collapse_sum(d[e])
            return d
            
          

#genegraph=collapse_sum(genegraph)
#print(genegraph)

level = ["kingdom","phylum","class","order_"]

seps = list()

def add_to_seps(parentage,d):
    seps.append(level[len(parentage)],parentage[-1],list(sum_files(d)))
    

def split_down(d,parentage = []):
    total=sum_down(d)
    # print(len(parentage)*4*"-",total)
    if(total)>500 or len(parentage)<=1:
        #MUST CUT
        if len(parentage)==4:
            #End of the line
            # print(d)
            print(parentage,"::",total,len(sum_files(d)))
            add_to_seps(parentage,d)
            return True
        else:
            # print(list(d.keys()))
            totals = list((sum_down(d[i]),i) for i in d.keys())
            summable = list()
            subtotal = 0
            for (s,i) in totals:
                # if(s>1000):
                # print(s,i)
                # print(total-s)
                
                if(not split_down(d[i],parentage+[i])):
                    # print(i,"could not split with",s)
                    summable.append(i)
                    subtotal+=s
                else:
                    total-=s
            if(summable):
                print(parentage,":",summable,subtotal,len(set_collapse((sum_files(d[i]) for i in summable))))
                
                add_to_seps(parentage,d)
            return True
    else:
        # print("total",total)
        return False
#split_down(genegraph)

def select_all_orders(d, parentage = []):
    if(len(parentage)==2):
        return set(d.keys())
    else:
        orders = set()
        for k in d.keys():
            orders=orders.union(select_all_orders(d[k],parentage+[k]))
        return orders
print(select_all_orders(genegraph))