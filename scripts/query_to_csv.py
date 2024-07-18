from rois.models import Image
from django.conf import settings
import datetime
import pytz
import numpy as np
import glob
import os
import sys
from loguru import logger

sys.path.append('/home/rimsadmin/software/rims/rois')
import xmlsettings


def convert_to_pix(val, cam):
    """
    convert from mm to pix using appropriate camera resolution
    :param val: measurement in millimeters [str]
    :param cam: flag indicating which camera to use [str]
    :return: out: number of pixels [int]
    """

    cam_res = 0.89/1000  # Chiton resolution c. Mar 2023
    out = np.floor(float(val) / cam_res)

    return int(out)


def run(*args):
    """
    Convert image paths from query into rows of csv
    """

    # load the config file defined in args
    cfg = xmlsettings.XMLSettings(args[0])

    # naive datetime objects
    start_hour = datetime.datetime.fromisoformat(cfg.get("StartTime"))
    end_hour = datetime.datetime.fromisoformat(cfg.get("EndTime"))
    logger.info(f"Start: {start_hour}, end: {end_hour}")

    # get the path to symlink to
    outfile = cfg.get("OutFile")


    # get the size and aspect parameters
    min_len = convert_to_pix(cfg.get("MinSize"), cfg.get("CameraName"))
    max_len = convert_to_pix(cfg.get("MaxSize") , cfg.get("CameraName"))
    min_as = float(cfg.get("MinAspect"))
    max_as = float(cfg.get("MaxAspect"))

    img_list = Image.objects.filter(timestamp__gte=start_hour,
                               timestamp__lt=end_hour,
                               camera__name=cfg.get("CameraName"),
                               major_axis_length__gte=min_len,
                               major_axis_length__lt=max_len,
                               aspect_ratio__gte=min_as,
                               aspect_ratio__lt=max_as)

    logger.info(f"save {len(img_list)} ROI paths to {outfile}")
    
    with open(outfile,"w") as f:

        for img in img_list:
            tmp = os.path.join(settings.BASE_DIR, f"{img.get_image_path()}.jpg")
            f.write(tmp+"\r\n")
            


    logger.info("completed")
