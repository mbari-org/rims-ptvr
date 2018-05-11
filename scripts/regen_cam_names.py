from rois.models import Image, PlanktonCamera

def run():
    count = 0
    images = Image.objects.all()
    spc = PlanktonCamera.objects.get(name='SPC')
    spcp = PlanktonCamera.objects.get(name='SPCP')
    for img in images.iterator():

        meta = img.explode_id()
        if (meta['camera'] == 'SPC'):
            img.camera = spc
        if (meta['camera'] == 'SPCP'):
            img.camera = spcp
        img.save()
        count = count + 1
        if count % 10000 == 0:
            print "processed " + str(count) + " images."
