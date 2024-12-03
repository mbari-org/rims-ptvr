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

    if cam == "PTVR02HM":
        cam_res = 0.89/1000
    elif cam == "PTVR02LM":
        cam_res = 7.0/1000
    else:
        logger.warning("No Matching camera type found, using 60um/pixel")
        cam_res = 60.0/1000

    logger.info("Camera resolution: " + str(cam_res*1000) + "um/pixel")

    cam_res = 0.89/1000 
    out = np.floor(float(val) / cam_res)

    return int(out)


def run(*args):
    """
    Query RIMS for a subset of ROIs and save ROI image path and fields as rows in csv. 
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

    # This is the general RIMS query format.
    # Filter the set of all ROIs based on the input parameters from the xml.
    # There are lots of ways to get more specific with the filters
    # Here we only filter on time, size, and aspect ratio
    img_list = Image.objects.filter(timestamp__gte=start_hour,
                               timestamp__lt=end_hour,
                               camera__name=cfg.get("CameraName"),
                               major_axis_length__gte=min_len,
                               major_axis_length__lt=max_len,
                               aspect_ratio__gte=min_as,
                               aspect_ratio__lt=max_as)

    logger.info(f"exporting {len(img_list)} ROIs to {outfile}")
    
    # Open output csv
    with open(outfile,"w") as f:

        # Loop over the images returned from the query
        for img in img_list:
            
            # Extract the ROI fields from the ROI object
            image_path = os.path.join(settings.BASE_DIR, f"{img.get_image_path()}.jpg")
            timestamp = img.timestamp
            maj_length = img.major_axis_length
            min_length = img.minor_axis_length
            aspect_ratio = img.aspect_ratio
            depth = img.depth
            lat = img.latitude
            lon = img.longitude
            temperature = img.temperature
            chl = img.chlorophyll
            
            # Format the fields into a csv row
            output_string = (
                    str(image_path) + ',' + 
                    str(timestamp) + ',' +
                    str(maj_length) + ',' +
                    str(min_length) + ',' +
                    str(aspect_ratio) + ',' + 
                    str(depth) + ',' +
                    str(lat) + ',' + 
                    str(lon) + ',' +
                    str(temperature) + ',' +
                    str(chl)
            )
            
            # Write the row to the file
            f.write(output_string+"\r\n")
            


    logger.info("completed")
