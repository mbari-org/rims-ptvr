

##### Step 1 - Loading RIMS images into dirs for training

# Loop through the provided list of labels
#   For each label:
#       Query RIMS to get list of images (apply size and date range filters as well)
#       Create a subdir for the label
#       for each Image
#           get the path to the zip archive
#           Extract the _original.tiff version of the image to the subdir

##### Step 2 - Train model

# Load resnet-18 and prune the last layer
# Load the labels and images into training and validation sets for pytorch
# Train 
# Save model and training stats to disk

# Standard imports
import datetime
import pytz
import numpy as np
import glob
import os
import sys
from loguru import logger
from rois.models import Image
from django.conf import settings


sys.path.append('/home/rimsadmin/software/rims-ptvr/rois')

# importing the zipfile module 
from zipfile import ZipFile 

def extract_from_zip(zip_path, filename, dest_path):
    """ extract a file from a zip archive and store it at dest_path """
    # loading the temp.zip and creating a zip object 
    with ZipFile(zip_path, 'r') as zObject: 
  
        # Extracting specific file in the zip 
        # into a specific location. 
        zObject.extract( filename, path=dest_path) 
    zObject.close()
    
def extract_images(image_list, base_path, subdir):
    """ Loop through results from a RIMS Image query and extract _original.tif versions of each image"""
    for img in image_list:
        
        filename = f"{img.get_image_path()}_original.tif"
        zip_path = os.path.join(settings.BASE_DIR, f"{img.get_image_path()}.zip")

        if os.path.exists(zip_path):
            extract_from_zip(zip_path, filename, subdir)
        else:
            logger.info(f"cannot find: {img.get_image_path()}") 
            
def run(*args):
    """
    copys images and builds resnet-18 model based on predefined labels
    """