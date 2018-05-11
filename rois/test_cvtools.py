import time
import cvtools
import pstats
import cProfile
import multiprocessing

def worker(num):
    #img = cvtools.import_image('.','SPCP2-1463011592-007448-000-1516-1328-112-96_raw.tif')
    img = cvtools.import_image('.','SPC2-1525378331-176841-003-3000-1132-120-184_raw.tif')
    img_c_8bit = cvtools.convert_to_8bit(img)
    cProfile.runctx("cvtools.extract_features(img_c_8bit,img,save_to_disk=False,abs_path='.',file_prefix='test_img_output_tt')",globals(),locals(),'prof%d.prof' %num)


for i in range(12):
    p = multiprocessing.Process(target=worker,args=(i,))
    p.start()

time.sleep(3)
for i in range(12):
    s = pstats.Stats('prof%d.prof' %i)
    s.strip_dirs().sort_stats("cumtime").print_stats()
