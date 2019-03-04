# hondabox.py

from PIL import Image

RES_LIST = {
    '720p': (1280, 720),
    'WGA': (800, 480)
    'VGA': (640, 480)
}

def auto_scale(origimage, resolution):
    """Scale origimage according to resolution string"""
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

def solid_color(color, resolution):
    """Create image of color string according to resolution string"""
    size = RES_LIST[resolution]
    finalimage = Image.new('RGB', size, color)
    return finalimage
