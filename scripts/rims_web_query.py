import urllib.request
import json

# Build a RIMS URL

base_url = "http://deeprip.shore.mbari.org/"

url_params = [
    "http://deeprip.shore.mbari.org/rims-ptvr/rois/images",    # base address, no trailing "/"
    "PTVR02HM",                                                 # camera name
    "1714982400000",                                            # start unixtime in ms
    "1715414399000",                                            # end unixtime in ms
    "0",                                                        # legacy start hours
    "24",                                                       # legacy end hours
    "0",                                                        # min depth (meters)
    "300",                                                      # max depth (meters)
    "5000",                                                     # images to return
    "581",                                                      # min length in pixels
    "5814",                                                     # max length in pixels
    "0.05",                                                     # min aspect ratio
    "1",                                                        # max aspect ratio
    "clipped",                                                  # exclude clipped images
    "randomize",                                                # return images in randomized order
    "skip",                                                     # legacy
    "Any",                                                      # comma separated list of labels to match
    "anytype",                                                  # legacy
    "Any",                                                      # comma separated list of tags to match
    "Any",                                                      # comma separated list of annorators to match
]

# Build the URL
url = "/".join(url_params) + "/"
print(url)

# Send requet to RIMS and receive the result
response = urllib.request.urlopen(url)

# extract the list of image objects from the result
result = json.loads(response.read())
imgs =  result['image_data']['results']

# disply the fields for the first image
print(imgs[0])

# Form URL to image to download (also can use .zip to get all of the images)
image_url = base_url + imgs[0]['image_url'] + '.jpg'
print(image_url)