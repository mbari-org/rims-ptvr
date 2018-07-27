from rois.models import Image

image_list = 'scripts/output.log'


def run(*args):


    with open(image_list,"r") as f:
        
        image_ids = f.readlines()


    missed = []

    for i, img in enumerate(image_ids):

        image_id = img.rstrip()

        im = Image.objects.filter(pk=image_id)
        if not im.exists():
            print str(i) + ' : ' + image_id
            missed.append(image_id)

    with open('/home/ptvradmin/missed_images.txt',"w") as f:
        for img in missed:
            f.write(img+'\n')




