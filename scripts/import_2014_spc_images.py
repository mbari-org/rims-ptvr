from rois.models import Image
import glob
import os
import sys

def run(*args):

    dir_prefix = args[0]
    
    # Loop over all images from SPCP 2014 year 
    # assuming they live in: /media/labdata1/SPC/phytocam/data
    data_dir_list = glob.glob(
            '/media/labdata1/SPC/planktoncam/data/'+dir_prefix)

    for data_dir in data_dir_list:

        image_list = glob.glob(os.path.join(data_dir,'*.tif'))

        for image_path in image_list:

            try:

                # extract the image id
                image_name = image_path.split('/')[-1]
                
                # Don't import if image exists already
                if (Image.objects.filter(image_id = image_name).exists()):
                    print "Skipping image (exists): " + image_name 
                    continue
                
                # If it does not exist, import
                print "Importing " + image_name
                im = Image(image_id=image_name)
                im.import_image(data_dir)
                im.save()

            except:
                print "Exception in import image " + image_name
                print "Unexpected error:", sys.exc_info()[0]

