from rois.models import Image, PlanktonCamera

"""
Created Tue May 01, 2018

Adds camera, height, and width information to ROIs with missing fields.
Corrects issue created by accidental removal of last few lines of import image
function in Image model.

@author: Eric Orenstein
"""

def run():

    # get the missing images
    imgs = Image.objects.filter(camera__isnull=True)

    tot = imgs.count()

    # display the number of missing images
    print "number of images " + str(tot)

    # loop through the images
    flag = 0
    spc = 0
    spcp = 0
    for img in imgs:
        info = img.explode_id()
        img.camera = PlanktonCamera.objects.get(name=info['camera'])
        if info['camera'] == 'SPC2':
            spc += 1
        elif info['camera'] == 'SPCP2':
            spcp += 1

        img.image_width = info['width']
        img.image_height = info['height']

        img.save()

        flag += 1

        if flag%10000 == 0:
            print "done with " + str(flag) + " of " + str(tot)  

    print "number of SPC images: " + str(spc)
    print "number of SPCP images: " + str(spcp)
