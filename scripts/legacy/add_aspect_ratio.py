from rois.models import Image, Tag
import glob
import os
import sys
import time
from multiprocessing import Pool

def do_update(img):

    if (img.major_axis_length != 0):
        img.aspect_ratio = float(img.minor_axis_length)/img.major_axis_length
    else:
        img.aspect_ratio = 0.0

    img.save()

def run(*args):

    qs = Image.objects.filter(camera__name=args[0],aspect_ratio=0.0)
    
    # map import to 8 threads rather than single loop,
    # Yay!!
    p = Pool(4)
    p.map(do_update,qs)

    #for image_path in image_list:

    #    do_import(image_path)
