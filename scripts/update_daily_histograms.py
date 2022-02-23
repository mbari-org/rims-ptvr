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
    tday = datetime.date.today()
    start_hour = datetime.datetime(
            year=tday.year,
            month=tday.month,
            day=tday.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=pytz.UTC
    )

    # Extract the other settings from argumnts
    # assumes mm units for length
    min_length = float(args[1].split(',')[0])/(7.38/1000)
    max_length = float(args[1].split(',')[1])/(7.38/1000)
    length_inc = float(args[1].split(',')[2])/(7.38/1000)
    min_aspect = float(args[2].split(',')[0])
    max_aspect = float(args[2].split(',')[1])
    aspect_inc = float(args[2].split(',')[2])

    # Create ranges for histograms
    length_bins = np.arange(min_length,max_length,length_inc)
    aspect_bins = np.arange(min_aspect,max_aspect,aspect_inc)

    
    cam = Camera.objects.get(name=args[0])

    t1 = start_hour - datetime.timedelta(days=1)

    t2 = start_hour
    # Get or create the object
    daily_hist,created  = DailyHistograms.objects.get_or_create(
        camera__name=cam,day=t1)
    daily_hist.camera = cam
    daily_hist.day = t1
        
    # retrive queryset
    values_list = Image.objects.filter(timestamp__gte=t1,
            timestamp__lt=t2,
            camera__name=cam.name).values_list('major_axis_length',
            'aspect_ratio')

    # Process
    major_lengths = np.array(values_list)[:,0]
    aspect_ratios = np.array(values_list)[:,1]
    daily_hist.total_rois = major_lengths.size
    
    # update display
    print "Date Range: " + str(t1) + " to " + str(t2)
    print "Found " + str(daily_hist.total_rois) + " rois."
    
    if len(values_list) == 0:
        daily_hist.save()
        return

    # Compute histograms
    daily_hist.length_bins = length_bins.tolist()
    daily_hist.aspect_bins = aspect_bins.tolist()
    length_counts = np.histogram(major_lengths,length_bins)
    aspect_counts = np.histogram(aspect_ratios,aspect_bins)

    daily_hist.length_counts = length_counts[0].tolist()
    daily_hist.aspect_counts = aspect_counts[0].tolist()



    # Save 
    daily_hist.save()

    print "Saved to db."

