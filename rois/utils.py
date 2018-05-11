# -*- coding: utf-8 -*-
"""
Created Tues. 11/07/17

Utility file for functions to be called in various Django files
"""

import calendar
import pytz
import datetime
import numpy as np

def convert_date(in_time):
    """
    Converts date in unix time in http format to utc in appropriate format for
    database query (including daylight savings check). Computes based on if
    query during dst or not.

    :param in_time: unix time in http format read from url request (in PST)
    :return out_ob: converted unix time for datebase query
    
    """
    
    # define the time zone
    tzone = pytz.timezone('America/Los_Angeles')
    
    # create the datetime object from the query time (divide by 1000 for http
    # format)
    in_ob = datetime.datetime.fromtimestamp(int(in_time)/1000)
        
    # localize it
    start_ob = tzone.localize(in_ob)
    
    # add an hour if query is in dst
    if start_ob.timetuple().tm_isdst == 1:
        hour_offset = 7*3600 - 8*3600
    else:
        hour_offset = 0
    
    # convert to datetime object with utc 
    out_ob = datetime.datetime.fromtimestamp(int(in_time)/1000 + hour_offset,
            tz=pytz.utc)

    return out_ob
