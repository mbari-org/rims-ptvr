from rois.models import Image
import datetime
import pytz
import numpy as np
import glob
import os
import sys

sys.path.append('/home/ptvradmin/virtualenvs/planktivore/planktivore/rois')
import xmlsettings


def local2utc(start_time, end_time, dst=False):
    """
    convert datetime range in Pacific time to UTC
    :param start_time: datetime in 'YYYY-MM-DD HH:MM:SS'
    :param end_time: datetime in 'YYYY-MM-DD HH:MM:SS'
    :param dst: flag indicating daylight savings time
    :return: utc_start, utc_end - datetime objects in utc
    """

    utc_start = pytz.timezone('America/Los_Angeles').localize(
        datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
    utc_end = pytz.timezone('America/Los_Angeles').localize(
        datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'))

    # Add 3600 to for daylight savings time
    if dst:
        utc_start = utc_start + datetime.timedelta(hours=1)
        utc_end = utc_end + datetime.timedelta(hours=1)

    # convert to datetime object in utc
    utc_start = utc_start.astimezone(pytz.utc)
    utc_end = utc_end.astimezone(pytz.utc)

    return utc_start, utc_end


def utc2local(dt):
    """
    convert datetime object in UTC to Pacific
    :param dt: datetime object in UTC
    :param dst: flag indicating daylight savings time
    :return: out: date string in Pacific 'YYYY-MM-DD HH:MM:SS'
    """
    temp = dt.astimezone(pytz.timezone('America/Los_Angeles'))
    out = temp.strftime('%Y-%m-%d %H:%M:%S')
    """
    if dst:
        dt = dt - datetime.timedelta(hours=1)

    out = dt.astimezone(pytz.timezone('America/Los_Angeles')) - datetime.timedelta(minutes=59)
    out = out.strftime('%Y-%m-%d %H:%M:%S')
    """
    return out

def make_timestamp(dt):
    """
    take datetime string in utc and make into utc datetime object
    :param dt: string in 'YYYY-MM-DD HH:MM:SS'
    :return: dt_out [datetime object]
    """
    temp = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    out = pytz.utc.localize(temp)

    return out

def convert_to_pix(val, cam):
    """
    convert from mm to pix using appropriate camera resolution
    :param val: measurement in millimeters [str]
    :param cam: flag indicating which camera to use [str]
    :return: out: number of pixels [int]
    """
    cam_res = [7.38 / 1000, 0.738 / 1000]

    # convert minLen and maxLen to pixels from mm
    if cam == 'SPC2':
        out = np.floor(float(val) / cam_res[0])
    elif cam == 'SPCP2':
        out = np.floor(float(val) / cam_res[1])
    else:
        print "unknown camera flag in convert_to_pix"

    return int(out)


def run(*args):
    """
    This version written to split the value list every million images
    12/12/17
    """

    # load the config file defined in args
    cfg = xmlsettings.XMLSettings(args[0])
    #start_hour, end_hour = local2utc(cfg.get("StartTime"), cfg.get("EndTime"), dst=cfg.get("dst"))
    start_hour = make_timestamp(cfg.get("StartTime"))
    end_hour = make_timestamp(cfg.get("EndTime"))
    ch = end_hour - start_hour
    change = ch.seconds

    # get number of hours
    num_hours = change/3600

    # get number of days
    #num_days = num_hours/24
    num_days = ch.days
    flag = 0

    # get the size and aspect parameters
    min_len = convert_to_pix(cfg.get("MinSize"), cfg.get("CameraName"))
    max_len = convert_to_pix(cfg.get("MaxSize") , cfg.get("CameraName"))
    min_as = float(cfg.get("MinAspect"))
    max_as = float(cfg.get("MaxAspect"))

    val_list = Image.objects.filter(timestamp__gte=start_hour,
                               timestamp__lt=end_hour,
                               camera__name=cfg.get("CameraName"),
                               major_axis_length__gte=min_len,
                               major_axis_length__lt=max_len,
                               aspect_ratio__gte=min_as,
                               aspect_ratio__lt=max_as).values_list('image_id',
                                                                    'timestamp',
                                                                    'major_axis_length',
                                                                    'minor_axis_length',
                                                                    'aspect_ratio')
    
    
    dirname = cfg.get("OutFile")
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    
    amt = len(val_list)
    for ii in range(0, len(val_list), 1000000):
        temp = val_list[ii:ii+1000000]
        out_ids = [item[0] for item in temp]
        out_list = [item[1::] for item in temp]

        date_col = [utc2local(item[0]) for item in out_list]

        np.asarray(out_list)
        out_list = np.delete(out_list, [0], axis=1)
        out_list = np.insert(out_list, 0, date_col, axis=1)
        bn_list = cfg.get("CameraName") +'_' + date_col[-1].split(' ')[0] + '_' + date_col[0].split(' ')[0] + '.csv'
        bn_ids = cfg.get("CameraName") +'_' + date_col[-1].split(' ')[0] + '_'+ date_col[0].split(' ')[0] + '_imageIds.csv'

        np.savetxt(os.path.join(dirname,bn_list), out_list, fmt="%s", delimiter=",")
        np.savetxt(os.path.join(dirname,bn_ids), out_ids, fmt="%s", delimiter=",")

        print 'done with ' + str(ii+1000000) + ' of ' + str(amt)
    """
    # bin by day
    for day in range(0, num_days+1):
        t1 = start_hour + datetime.timedelta(days=day)
        t2 = t1 + datetime.timedelta(days=1)

        val_list = Image.objects.filter(timestamp__gte=t1,
                                   timestamp__lt=t2,
                                   camera__name=cfg.get("CameraName"),
                                   major_axis_length__gte=min_len,
                                   major_axis_length__lt=max_len,
                                   aspect_ratio__gte=min_as,
                                   aspect_ratio__lt=max_as).values_list('timestamp',
                                                                        'major_axis_length',
                                                                        'minor_axis_length',
                                                                        'aspect_ratio')
        
        # get date string in local time for directory name
        out_dt = val_list[0][0]
        datestring = utc2local(out_dt) 
        #dirname = os.path.join(cfg.get("OutFile"), datestring.split(' ')[0])
        dirname = cfg.get("OutFile")

        # convert datetime object to string
        date_col = [item[0].strftime('%Y-%m-%d %H:%M:%S') for item in val_list]
        #date_col = [utc2local(item[0]) for item in val_list]

        # make list of tuples array, remove old datetime objects, replace with
        # string
        np.asarray(val_list)
        val_list = np.delete(val_list, [0], axis=1)
        val_list = np.insert(val_list, 0, date_col, axis=1)
        
        # make new directory if need be
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        
        basename = cfg.get("CameraName") +'_' + datestring.split(' ')[0] + '.csv'
        outname = os.path.join(dirname, basename)

        np.savetxt(outname, val_list, fmt='%s', delimiter=",")
    
       # if hour % 24 == 0:
       #     print 'done with ' + str(flag) + ' of ' + str(num_days)
       #     flag += 1
        
        print 'Done with ' + str(flag) + ' of ' + str(num_days)

        flag += 1

        """
