from rois.models import Image, Camera
from roistats.models import DailyHistograms
import datetime
import pytz
import numpy as np
import glob
import os
import sys

def run(*args):

    print args
    start_hour = datetime.datetime(
            year=int(args[0].split('/')[2]),
            month=int(args[0].split('/')[0]),
            day=int(args[0].split('/')[1]),
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=pytz.UTC
    )

    # Extract the other settings from argumnts
    # assumes mm units for length
    if args[1] == 'SPC2':
        min_length = float(args[2].split(',')[0])/(7.38/1000)
        max_length = float(args[2].split(',')[1])/(7.38/1000)
        length_inc = float(args[2].split(',')[2])/(7.38/1000)
    else:
        min_length = float(args[2].split(',')[0])/(0.738/1000)
        max_length = float(args[2].split(',')[1])/(0.738/1000)
        length_inc = float(args[2].split(',')[2])/(0.738/1000)

    min_aspect = float(args[3].split(',')[0])
    max_aspect = float(args[3].split(',')[1])
    aspect_inc = float(args[3].split(',')[2])

    # Create ranges for histograms
    length_bins = np.arange(min_length,max_length,length_inc)
    aspect_bins = np.arange(min_aspect,max_aspect,aspect_inc)

    
    cam = Camera.objects.get(name=args[1])

    t1 = start_hour

    t2 = t1 + datetime.timedelta(days=1)
    # Get or create the object
    
    # retrive queryset
    values_list = Image.objects.filter(timestamp__gte=t1,
            timestamp__lt=t2,
            camera__name=cam.name).values_list('major_axis_length',
            'aspect_ratio')

    # Process
    major_lengths = np.array(values_list)[:,0]
    aspect_ratios = np.array(values_list)[:,1]
    total_rois = major_lengths.size
    
    # update display
    print str(t1) + " found " + str(total_rois) + " rois."
    
    if len(values_list) == 0:
        print "no rois found."
        return

    # Compute histograms
    length_bins = length_bins.tolist()
    aspect_bins = aspect_bins.tolist()
    length_counts = np.histogram(major_lengths,length_bins)
    aspect_counts = np.histogram(aspect_ratios,aspect_bins)

    print length_counts[0].tolist()
    print length_counts[1]*.738


