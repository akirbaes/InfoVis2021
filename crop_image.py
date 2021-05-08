from PIL import Image
import os.path
import sys
from statistics import mode

def get_background_color(image):
    #For pixel-art with solid background
    #Looks at all the 4 corners
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
    
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
                    im = Image.open(pathname)
                    width,height=im.size
                    if(width==1920 and height==1440):
                        #300 dpi : 45 x  263 y
                        xborders = 45
                        yborders = 263
                    else:
                        xborders = 45
                        yborders = 263
                    new_width = width-xborders*2
                    new_height = height-yborders*2
                    
                    bg = get_background_color(im)
                    out = im.copy()
                    out = out.resize((new_width,new_height),resample=Image.NEAREST)
                    out.paste(bg,(0,0,new_width,new_height))
                    out.paste(im,(-xborders,-yborders))
                    out.save(path+"/../"+os.path.basename(path)+"_cropped/"+name)

            