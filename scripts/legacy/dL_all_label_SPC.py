from rois.models import Image
from rois.models import Label
import os
import sys
from cv2 import imwrite, imread, IMREAD_UNCHANGED

"""
Loops through all available user labels in the database and copies all the images to a new directory for later download
"""

def run():
    # this is where all the original rois are stored on the server
    in_path = "/home/spcadmin/virtualenvs/planktonview2/static/roistore"
    
    # this is where all the copied rois will be saved
    outPath = '/home/spcadmin/virtualenvs/planktonview2/all_labelData'
    # gets all the unique labels
    names = Label.objects.all().values('name')
    
    # cleans up the names
    names = [str(item['name']) for item in names]
    
    # loop through each name, create a queryset, and copy the images. 
    flag = 0
    for nn in names:
        # create the query set    
        labelSet = Image.objects.filter(user_labels__name=nn)
        
        if ' ' in nn:
            nn = nn.replace(' ','_')
        if '-' in nn:
            nn = nn.replace('-','_')
            
        where = os.path.join(outPath,nn)
        os.mkdir(where)
        
        for item in labelSet:
            # get the appropriate file path
            ptf = os.path.join(in_path,str(item.id_to_path()), str(item.image_id).split(".")[0]+".png")
            
            # read the file
            img = imread(ptf, IMREAD_UNCHANGED)
            
            # save as PNG
            imwrite(os.path.join(where, str(item.image_id).split(".")[0]+".png"), img)
            
        print 'Done with ' + nn +'. ' + str(flag) + ' of ' + str(len(names))
        flag += 1


"""
if __name__ == '__main__':
    stuff = os.getcwd()
    stuff = os.path.split(stuff)[0]
    outPath = os.path.join(stuff,'all_labelData')
    os.mkdir(outPath)
    run(outPath)
    
"""
