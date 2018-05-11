from rois.models import Image
import datetime
import pytz
import numpy as np
import glob
import os
import sys

def run():

    # Get the count in various size bins over a set of hours
    
    # define the start date. This first day the newest version went in the
    # water is 3/13/15
    # start_day = datetime.date(year=int(args[0].split('/')[2]),month=int(args[0].split('/')[0]),day=int(args[0].split('/')[1]))
    start_hour = datetime.datetime(
        year=2015,
        month=03,
        day=13,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=pytz.UTC
        )
    
    end_hour = datetime.datetime(
        year=2015,
        month=9,
        day=01,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=pytz.UTC
        )
    
    num = Image.objects.filter(timestamp__gte=start_hour,
                               timestamp__lt=end_hour,
                               camera__name='SPC2').count()
    
    num2 = Image.objects.filter(timestamp__gte=start_hour,
                               timestamp__lt=end_hour,
                               camera__name='SPC2',
                               major_axis_length__gte=0.5*144,
                               major_axis_length__lt=3.5*144).count()
    
    print 'Total 3/13 - 9/1/15: ' + str(num)
    print 'Total 3/13 - 9/1/15, size 0.5-3.5 mm: ' + str(num2)
