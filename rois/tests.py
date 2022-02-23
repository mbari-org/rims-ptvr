from django.test import TestCase
from scripts.import_images_from_dir import do_import, run

# Create your tests here.
class ImportTestCase(TestCase):
    run('rois/test_images', 'rois/default_proc_settings.json')
