from rois.models import Image, ProcSettings, LabelSet, TagSet, Tag, Label
import glob
import os
import sys
import time
from loguru import logger
from multiprocessing import Pool, cpu_count
from rois.file_name_formats import FileNameFmt, ChitonFileNameFmt

def do_import(import_data):
    
    django.db.close_old_connections()

    data_dir = import_data['data_dir']
    image_path = import_data['image_path']
    proc_settings = import_data['proc_settings']

    # skip images that may still be uploading
    if os.stat(image_path).st_atime >= (time.time() - 1):
        return

    # skip images that have zero file size
    if os.path.getsize(image_path) <= 0:
        logger.warning(image_path + " file size is <= 0.")
        return

    # Otherwise insert into DB
    image_name = os.path.basename(image_path)  # get the image name
    #logger.debug(image_path)
    try:
        
        # set file name parser
        if proc_settings.json_settings['file_name_fmt'] == 'Chiton':
            fnf = ChitonFileNameFmt()
        else:
            fnf = FileNameFmt()
            
        # Get the image meta data from filename
        fnf.parse_filename(image_name)

        # start processing timer...
        start_time = time.time()

        # Don't import if image exists already
        #print "Importing " + image_name
        already_imported = True
        im = Image.objects.filter(image_id = image_name)
        if not im.exists():
            already_imported = False
            im = Image(image_id=image_name)
       
        else:
            im = im[0]
            #print image_name + " already exists in db, will reprocess..."
            logger.debug(image_name + " already exists in db, skipping...")
            return
            
        search_time = time.time()-start_time
        # read and process the image
        start_time = time.time()
        im.import_image(data_dir,proc_settings)
        proc_time = time.time()-start_time
        
        start_time = time.time()
        #if not im.is_clipped and not already_imported:
        im.save()
        save_time = time.time()-start_time
        # Add Clipped Image tag is the image may be clipped
        if (im.is_clipped):
            ci = Tag.objects.get(name='Clipped Image')
            logger.warning(image_name + " is clipped.")
            im.tags.add(ci)
            im.save()
                
        # Remove the image
        #os.remove(image_path)
        
        logger.info(image_name + " : " + str(search_time) + "," + str(proc_time) + "," + str(save_time))

    except Exception as e:
        logger.error("Exception in import image " + image_name)
        logger.error("Unexpected error:", sys.exc_info()[0])
        logger.error("Exception: " + str(e))
        return
    
def find_all_images(data_dir):
    # List and group various image types
    image_list_raw1 = glob.glob(os.path.join(data_dir,'*[0-9].tif'))
    image_list_raw2 = glob.glob(os.path.join(data_dir,'*[0-9]_raw.tif'))
    image_list_png = glob.glob(os.path.join(data_dir,'*[0-9].png'))
    image_list_jpg = glob.glob(os.path.join(data_dir,'*[0-9].jpg'))
    
    return image_list_raw1 + image_list_raw2 + image_list_png + image_list_jpg

def load_proc_settings(proc_settings_file):
    # load settings and create new entry if needed or load entry
    proc_settings = ProcSettings()
    proc_settings.load_settings(proc_settings_file)
    ps = ProcSettings.objects.filter(name = proc_settings.name)
    if not ps.exists():
        proc_settings.save()
    else:
        proc_settings = ps[0]
    
    #populate settings from json
    proc_settings.create()
    
    return proc_settings
    

def run(*args):
    
    if len(args) < 2:
        logger.critical("Please pass the source directory and proc settings path as arguments.")
        exit()
    
    # modified to walk a directory of image directories
    base_dir = args[0]
    dir_list = glob.glob(os.path.join(base_dir,'*[0-9]'))
    
    # load or select proc_settings
    proc_settings_file = args[1]
    proc_settings = load_proc_settings(proc_settings_file)
    
    logger.info("Starting import...")
    logger.info("Found " + str(len(dir_list)) + " directories...")
    
    for data_dir in dir_list:

        image_list = find_all_images(data_dir)
        
        # Populate packages to send to map
        import_list = []
        for img in image_list:
            
            import_data = {}
            import_data['data_dir'] = data_dir
            import_data['image_path'] = img
            import_data['proc_settings'] = proc_settings
            
            import_list.append(import_data)
            
        logger.info("Importing from " + data_dir)
        logger.info("Found " + str(len(image_list)) + " images to import...")

        # Single process mode
        #for ii in import_list:
        #    do_import(ii)
        
        # Multiprocess mode
        start_time = time.time()
        p = Pool(processes=48)
        logger.info("mapping to cores...")
        p.map(do_import,import_list)
        logger.info("mapped.")
        p.close()
        logger.info("closed.")
        p.join()
        logger.info("finished with import.")
        roi_proc_time = len(image_list)/(time.time()-start_time)
        
        logger.info("Average ROI process time: " + str(roi_proc_time))

    #with open("/home/ptvradmin/roi_proc_stats.txt","a+") as f:
    #    f.write(str(time.time()) + "," + str(data_dir) + "," + str(roi_proc_time) + "\n")


