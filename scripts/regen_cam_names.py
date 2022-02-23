from rois.models import Image, Camera

def run():
    count = 0
    images = Image.objects.all()
    spc = Camera.objects.get(name='SPC')
    spcp = Camera.objects.get(name='SPCP')
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
