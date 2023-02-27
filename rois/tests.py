from django.test import TransactionTestCase
from scripts.import_images_from_dir import do_import, run

# Create your tests here.
class ImportTestCase(TransactionTestCase):
    run('/nvme-pool/rims/image_import/test_ayeris_to_rims', 'rois/default_proc_settings.json')

#class LargeImportTestCase(TestCase):
#    run('/home/rimsadmin/image_import', 'rois/default_proc_settings.json')
