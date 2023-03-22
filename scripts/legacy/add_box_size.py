from rois.models import Image
import datetime

d1 = datetime.datetime(2015,3,11)

qs = Image.objects.filter(timestamp__gte = d1)

for img in qs:
    meta = img.explode_id()
    img.image_width = meta['width']
    img.image_height = meta['height']
    img.save()
    print img.image_id
