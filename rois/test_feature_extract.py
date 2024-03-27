import cv2
import json
from cvtools import extract_features

settings_path = '/home/rimsadmin/software/rims-ptvr/rois/ptvr_proc_settings.json'
img_path = 'test_images/LRAH11_20240319T171632.263513Z_PTVR02LM_1222_486_2124_562_0_175_356_0_original.tif'

img = cv2.imread(img_path)
settings = json.load(open(settings_path))
extract_features(img,img,settings,save_to_disk=True,abs_path='test_images',file_prefix='test_output')