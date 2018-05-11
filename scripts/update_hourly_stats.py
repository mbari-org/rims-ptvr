from rois.models import Image, PlanktonCamera
from roistats.models import HourlyStats
import datetime
import pytz
import numpy as np
import glob
import os
import sys

def run(*args):

    print args
    start_day = datetime.date.today() - datetime.timedelta(days=1) 
    start_hour = datetime.datetime(
            year=start_day.year,
            month=start_day.month,
            day=start_day.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=pytz.UTC
    )
    
    cam = PlanktonCamera.objects.get(name=args[0])

    # Loop over all the days and compute stats
    n_hours = 24
    
    for hour in range(0,n_hours):


        t1 = start_hour + datetime.timedelta(hours=hour)

        t2 = t1 + datetime.timedelta(hours=1)

        # Get or create the object
        hourly_stats,created  = HourlyStats.objects.get_or_create(camera__name=cam,hour=t1)
        hourly_stats.camera = cam
        hourly_stats.hour = t1
        
        # retrive queryset
        values_list = Image.objects.filter(timestamp__gte=t1,
                timestamp__lte=t2,
                camera__name=cam.name).values_list('major_axis_length',
                'minor_axis_length')
        

        if len(values_list) == 0:
            hourly_stats.save()
            continue

        # Process
        major_lengths = np.array(values_list)[:,0]
        minor_lengths = np.array(values_list)[:,1]
        
        hourly_stats.total_rois = major_lengths.size
        hourly_stats.average_major_length = int(np.mean(major_lengths))
        hourly_stats.average_minor_length = int(np.mean(minor_lengths))
        hourly_stats.stddev_major_length = int(np.std(major_lengths))
        hourly_stats.stddev_minor_length = int(np.std(minor_lengths))
        hourly_stats.median_major_length = int(np.median(major_lengths))
        hourly_stats.median_minor_length = int(np.median(minor_lengths))

        # update display
        print str(t1) + " found " + str(hourly_stats.total_rois) + " rois."

        # Save 
        hourly_stats.save()
