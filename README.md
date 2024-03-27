# RIMS (Region of Interest Management System)

A framework for maganing and visualization images and/or Regions Of Interest (ROI) recorded by an imaging system with frontend tools to visualize mosaics of images filtered by size, datetime, and morphological features.

## Requirements

* python
* django
* postgresql
* gunicorn
* nginx

## Installation

### Preliminaries
Clone the RIMS repo and cd into it. From there follow the [Digital Ocean setup instructions](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04) for Django with Postgres, Nginx, and Gunicorn on Ubuntu 20.04.

### Install Python Packages
Install the following extra Django management functionality via pip

`$ pip install django-extensions django-mptt django-jquery django-rest-framework django-cors-headers`

Make sure to incude the apps in the `rims/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jquery',
    'django_extensions',
    'rest_framework',
    'corsheaders',
    'mptt',
    'rois',
]
```

Then install a few further packages for the image processing routines and pretty error logging.

`$ pip install opencv-python scikit-image loguru`

### Update service to reload
Tell gunicorn to automatically reload upon edit by changing `ExecStart` in `etc/systemd/gunicorn.service`

```
ExecStart=/home/rimsadmin/software/rims/rimsenv/bin/gunicorn \
	--access-logfile - \
	--workers 4 \
	--reload \
	--bind unix:/run/gunicorn.sock \
	rims.wsgi:application
```

## Tests
Run unit tests with Django's [https://docs.djangoproject.com/en/4.0/topics/testing/overview/](test features). In the ROIs directory write test models that will function in that framework:

```python
from django.test import TestCase
from scripts.import_images_from_dir import do_import, run

# Create your tests here.
class ImportTestCase(TestCase):
    run('rois/test_images', 'rois/default_proc_settings.json')
```

Put a small set of images into the `rois/test_images` file and make sure the json settings file exists in the correct place. There are four images included in static/examples/test_images that can be used for this purpose. Currently these images will be removed each time you run the test import.

From the command line while in the database virtual environment run:

`$ python manage.py test rois.tests`

This command should spin up a small test database and run the `import_images_form_dir.py` script

## Import images from directory

`$ ./manage.py runscript import_images_from_dir --script-args /path/to/temp/image_directory /path/to/processing/settings.json`

Where `/path/to/temp/image_directory` is a directory of raw images to import, and `/path/to/processing/settings.json` is the path to the proc_settings JSON file, typically in rois/default_proc_settings.json

## Access web browser
Access the user interface by going to [http://deeprip.shore.mbari.org/static/spcview/spcview.html#](http://deeprip.shore.mbari.org/static/spcview/spcview.html#) 

You should see a mosaic like the one below

![example](/static/examples/browser.jpg)