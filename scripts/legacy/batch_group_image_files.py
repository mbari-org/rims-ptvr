import glob
import os
import sys
import time


dir_prefix = sys.argv[1]
    
# Loop over all images from SPCP 2014 year 
# assuming they live in: /media/labdata1/SPC/phytocam/data

data_dir_list = glob.glob(
        '/home/spcadmin/virtualenvs/planktonview2/static/roistore/'+dir_prefix+'/*')

for data_dir in data_dir_list:

    print data_dir
    sub_dir_list = glob.glob(os.path.join(data_dir,'*'))

    for sub_dir in sub_dir_list:

        print sub_dir
        image_list = glob.glob(os.path.join(sub_dir,'*binary.png'))

        for image_path in image_list:


            try:

                # extract the image id
                image_name = image_path.split('/')[-1]
                image_prefix = image_name.split('_binary.png')[0]
                
                #print image_prefix

                image_prefix = os.path.join(os.path.dirname(image_path),image_prefix)
                    
                #print "Compacting " + image_prefix + '...'
                cmd = ('zip -mj ' + image_prefix + '.zip' + ' ' + 
                    image_prefix + '.png ' +
                    image_prefix + '_binary.png ' +
                    image_prefix + '_rawcolor.jpg')

                #print cmd
                os.system(cmd)
                #os.system('rm ' + image_prefix + '.png')
                #os.system('rm ' + image_prefix + '_binarypng')
                #os.system('rm ' + image_prefix + '_rawcolor.jpg')

                #print 'Done with ' + image_name + '.'

                
                #time.sleep(.1)
                
            except:
                print "Exception in compacting image " + image_name
                print "Unexpected error:", sys.exc_info()[0]

