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
    start_day = datetime.date(year=int(args[0].split('/')[2]),
            month=int(args[0].split('/')[0]),day=int(args[0].split('/')[1]))
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
    
    cam = PlanktonCamera.objects.get(name=args[1])

    max_aspect = float(args[3])

    # Loop over all the days and compute stats
    n_hours = int(args[2])
    
    for hour in range(0,n_hours):


        t1 = start_hour + datetime.timedelta(hours=hour)

        t2 = t1 + datetime.timedelta(hours=1)

        # retrive queryset
        values_list_all = Image.objects.filter(timestamp__gte=t1,
                timestamp__lte=t2,
                camera__name=cam.name,
                aspect_ratio__range=[max_aspect+0.05,1]
        ).values_list('major_axis_length',flat=True)
        
        values_list_filtered = Image.objects.filter(timestamp__gte=t1,
                timestamp__lte=t2,
                camera__name=cam.name,
                aspect_ratio__range=[0,max_aspect],
        ).values_list('major_axis_length',flat=True)
        

        # update display
        print str(t1) + "," + str(t2) + "," +  str(len(values_list_all)) + "," + str(len(values_list_filtered))
    
