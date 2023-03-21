import glob
from django.test import TransactionTestCase
from scripts.import_images_from_dir import do_import, run

# Create your tests here.
class ImportTestCase(TransactionTestCase):
    dl = glob.glob('/nvme-pool/rims/image_import/dec-2022-c1-m2/extracted_rois/*')
    for d in dl:
        run(d, 'rois/default_proc_settings.json')

#class LargeImportTestCase(TestCase):
#    run('/home/rimsadmin/image_import', 'rois/default_proc_settings.json')
