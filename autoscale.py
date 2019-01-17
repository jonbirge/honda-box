# autoscale.py

from PIL import Image

def auto_scale(origimage, resolution):
    """Scale origimage according to resolution in {'720p', 'WGA'}"""
    RES_LIST = {
        "720p": (1280, 720),
        "WGA": (800, 480)
    }
    final_width, final_height = RES_LIST[resolution]
    final_aspect = final_width/final_height
    width, height = origimage.size
    aspect = width/height
    if aspect > final_aspect:  # crop x
        int_width = int(final_height*aspect)
        intimage = origimage.resize((int_width, final_height), Image.ANTIALIAS)
        extrax = int_width - final_width
        finalimage = intimage.crop((extrax//2, 0, int_width - extrax//2, final_height))
    else:  # crop y
        int_height = int(final_width/aspect)
        intimage = origimage.resize((final_width, int_height), Image.ANTIALIAS)
        extray = int_height - final_height
        finalimage = intimage.crop((0, extray//2, final_width, int_height - extray//2))
    return finalimage
