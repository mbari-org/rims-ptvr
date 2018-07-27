from rois.models import Image, LabelSet, TagSet, Tag, Label
import glob
import os
import sys
import time
from multiprocessing import Pool

data_dir = '/home/ptvradmin/inputdata/caymans2017/EC3_SPC_Images_3-COLOR/'

def do_import(image_path):

    # skip images that may still be uploading
    if os.stat(image_path).st_atime >= (time.time() - 1):
        return

    # skip images that have zero file size
    if os.path.getsize(image_path) <= 0:
        print image_path + " file size is <= 0."
        return

    # Otherwise insert into DB
    try:

        # extract the image id
        image_name = image_path.split('/')[-1]
        start_time = time.time()
        # remove _raw from image id if it exists 
        from_raw = False
        if len(image_name.split('_raw')) > 1:
            image_name = image_name.split('_raw')[0] + '.tif'
            from_raw = True

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
            print image_name + " already exists in db, skipping..."
            return
            
        search_time = time.time()-start_time
        # read and process the image
        start_time = time.time()
        im.import_image(data_dir,from_raw)
        proc_time = time.time()-start_time
        
        start_time = time.time()
        #if not im.is_clipped and not already_imported:
        im.save()
        save_time = time.time()-start_time
        # Add Clipped Image tag is the image may be clipped
        # NOTE: we opt here to not save the clipped images in the dB
        #if (im.is_clipped):
        #    ci = Tag.objects.get(name='Clipped Image')
        #    print "Clipped Image"
        #    im.tags.add(ci)
        #    im.save()
                
        # Remove the image
        os.remove(image_path)
        
        print image_name + " : " + str(search_time) + "," + str(proc_time) + "," + str(save_time)

    except Exception, e:
        print "Exception in import image " + image_name
        print "Unexpected error:", sys.exc_info()[0]
        print "Exception: " + str(e)
        return

def run(*args):


    
    print "starting import..."

    image_list_raw1 = glob.glob(os.path.join(data_dir,'*[0-9].tif'))
    
    image_list_raw2 = glob.glob(os.path.join(data_dir,'*[0-9]_raw.tif'))

    image_list_png = glob.glob(os.path.join(data_dir,'*[0-9].png'))

    image_list_jpg = glob.glob(os.path.join(data_dir,'*[0-9].jpg'))
    

    image_list = image_list_raw1 + image_list_raw2 + image_list_png + image_list_jpg

    print "Found " + str(len(image_list)) + " images to import..."

    # map import to 12 threads rather than single loop,
    # Yay!!
    start_time = time.time()
    p = Pool(12)
    print "mapping to cores..."
    p.map(do_import,image_list)
    print "mapped."
    p.close()
    print "closed."
    p.join()
    print "finished with import."
    roi_proc_time = len(image_list)/(time.time()-start_time)
    with open("/home/ptvradmin/roi_proc_stats.txt","a+") as f:
        f.write(str(time.time()) + "," + str(data_dir) + "," + str(roi_proc_time) + "\n")


