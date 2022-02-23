from rois.models import Image, Camera
from roistats.models import DailyStats
import datetime
import pytz
import numpy as np
import glob
import os
import sys

def run(*args):

    cam = Camera.objects.get(name=args[0])

    end_day = datetime.date.today()
    start_day = end_day - datetime.timedelta(days=1)

    # Loop over all the days and compute stats
    n_days = (end_day-start_day).days
    
    for day in range(0,n_days):

        d1 = datetime.datetime.combine(
                start_day + datetime.timedelta(days=day),
                datetime.time()
        )
        d1 = pytz.UTC.localize(d1)
        d2 = datetime.datetime.combine(
                d1 + datetime.timedelta(days=1),
                datetime.time()
        )
        d2 = pytz.UTC.localize(d2)
        
        exists = DailyStats.objects.filter(
                    day=d1,camera__name=cam.name
                ).count()
        if (exists == 0):
            daily_stats = DailyStats()
            daily_stats.camera = cam
            daily_stats.day = d1
        else:
            print "Entry exists, updating..."
            daily_stats = DailyStats.objects.get(
                                day=d1,
                                camera__name=cam.name
                            )
        
        # retrive queryset
        values_list = Image.objects.filter(timestamp__gte=d1,
                timestamp__lte=d2,
                camera__name=cam.name).values_list('major_axis_length',
                'minor_axis_length')
        

        if len(values_list) == 0:
            daily_stats.save()
            continue

        # Process
        major_lengths = np.array(values_list)[:,0]
        minor_lengths = np.array(values_list)[:,1]
        
        daily_stats.total_rois = major_lengths.size
        daily_stats.average_major_length = int(np.mean(major_lengths))
        daily_stats.average_minor_length = int(np.mean(minor_lengths))
        daily_stats.stddev_major_length = int(np.std(major_lengths))
        daily_stats.stddev_minor_length = int(np.std(minor_lengths))
        daily_stats.median_major_length = int(np.median(major_lengths))
        daily_stats.median_minor_length = int(np.median(minor_lengths))

        # update display
        print str(d1) + " found " + str(daily_stats.total_rois) + " rois."

        # Save 
        daily_stats.save()
