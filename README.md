# RIMS (Region of Interest Management System)

A framework for maganing and visualization images and/or Regions Of Interest (ROI) recorded by an imaging system with frontend tools to visualize mosaics of images filtered by size, datetime, and morphological features.

## Requirements

* python
* django
* postgresql
* gunicorn
* nginx

## Installation
Clone and cd into this repo then follow the [Digital Ocean setup instructions](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04) for Django with Postgres, Nginx, and Gunicorn on Ubuntu 20.04. 

After confirming install per the Digital Ocean article, set up as There are some slight modifications and several extra packages that need to be installed via pip (both for image processing and extra db management tools).

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

### Install Python Packages for Image Processing

`pip install opencv-python scikit-image loguru`

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

-   Working on it...