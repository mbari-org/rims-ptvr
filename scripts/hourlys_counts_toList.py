from rois.models import Image
import datetime
import pytz
import numpy as np
import glob
import os
import sys

def run():

    # Get the count in various size bins over a set of hours
    
    # define the start date
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
        month=11,
        day=01,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=pytz.UTC
        )
        
    ch = end_hour - start_hour
    change = ch.days
    
    num_Hours = change*24
    
    sizeClasses = [0,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,10000]
    
    out = np.zeros([len(sizeClasses),num_Hours])
    for sz in range(1,len(sizeClasses)):
        for hour in range(0,num_Hours):
            t1 = start_hour + datetime.timedelta(hours=hour)
            t2 = t1 + datetime.timedelta(hours=1)
            
            num = Image.objects.filter(timestamp__gte=t1,
                                       timestamp__lt=t2,
                                       camera__name='SPC2',
                                       major_axis_length__gte=sizeClasses[sz-1]*144,
                                       major_axis_length__lt=sizeClasses[sz]*144).count()
            
            out[(sz-1),hour] = num
            
            if hour%100==0:
                print "done with " + str(hour) + ' of ' + str(num_Hours) + '(' + str(sz-1) + ' to ' + str(sz)+ ')'
                
    np.savetxt('/home/spcadmin/virtualenvs/planktonview2/spc2_hourly_counts.txt',out)
    
