from PIL import Image
import os.path
import sys
from statistics import mode
import numpy as np

def get_background_color(image):
    #For pixel-art with solid background
    #Looks at all the 4 corners
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
    
def detect_borders(im,from_the_middle=True):
    red=np.array([255,0,0,255],dtype=np.uint8)
    green=np.array([0,128,0,255],dtype=np.uint8)
    
    npimage=np.array(im)

    #print(img_arr)
    reds=np.where(np.all((npimage==red),axis=-1))
    greens=np.where(np.all((npimage==green),axis=-1))
    last_red = reds[1][-1],reds[0][-1]
    first_green = greens[1][0],greens[0][0]
    indices = *last_red, *first_green
    print(indices)
    origin=last_red
    end=first_green
    # xo,yo = origin
    # x,y = first_green
    # size = x-xo, y-yo
    # coordinates = zip(indices[0], indices[1])
    #origin = indices[np.argmin(indices)]
    #end = indices[np.argmax(indices)]
    print(":",origin,end)
    
    return origin[0],origin[1],end[0]-origin[0],end[1]-origin[1]
    
    
    
if __name__ == "__main__":
    import sys
    
    if(len(sys.argv)>1):
        path=sys.argv[1]
        try:
            os.mkdir(path+"/../"+os.path.basename(path)+"_cropped")
        except:
            pass
        for dirpath, dirnames, filenames in os.walk(path):
            for name in filenames:
                #for arg in sys.argv[1:]:
                if(name.endswith(".png")):
                    pathname =os.path.join(dirpath, name)
                    im = Image.open(pathname).convert("RGBA")
                    width,height=im.size
                    
                    borders = detect_borders(im)
                    xborders,yborders,new_width,new_height=borders
                    
                    # if(width==1920 and height==1440):
                        # #300 dpi : 45 x  263 y
                        # xborders = 45
                        # yborders = 263
                    # else:
                        # xborders = 45
                        # yborders = 263
                    # new_width = width-xborders*2
                    # new_height = height-yborders*2
                    
                    bg = get_background_color(im)
                    out = im.copy()
                    out = out.resize((new_width,new_height),resample=Image.NEAREST)
                    out.paste(bg,(0,0,new_width,new_height))
                    out.paste(im,(-xborders,-yborders))
                    out.save(path+"/../"+os.path.basename(path)+"_cropped/"+name)

            