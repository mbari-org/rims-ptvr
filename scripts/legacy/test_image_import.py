from rois.models import Image

def run():
    # Try to create and import a valid SPC image
    im = Image(image_id='SPCP-1407484364-000035-000-476-1256-72-56.tif')
    im.import_image('/media/labdata1/SPC/phytocam/data/1407484359')

    # Display some stats
    print "Image ID: " + str(im.image_id)
    print "Major Length: " + str(im.major_axis_length)
    print "Minor Length: " + str(im.minor_axis_length)
    print "Timestamp: " + str(im.timestamp)

    # Save into db
    im.save()

    # Get some info
    Image.objects.all()

    # The image auto id
    print "Image AUTOID: " + str(im.id)

    # delete the image from the db
    im.delete()

    # Get some info
    Image.objects.all()

    # to do remove the copied images from the image store
