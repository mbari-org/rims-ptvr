from rois.models import Image
import os
from cv2 import imwrite, imread, IMREAD_UNCHANGED

def run():
    in_path = "/home/spcadmin/virtualenvs/planktonview2/static/roistore"
    op1 = "/home/spcadmin/virtualenvs/planktonview2/oithona"
    op2 = "/home/spcadmin/virtualenvs/planktonview2/oithona_egg"
    op3 = "/home/spcadmin/virtualenvs/planktonview2/oithona_para"

    oith = Image.objects.filter(
        user_labels__name = "Oithona similis"
    ).exclude(
        user_labels__name = "Oithona similis_egg sacs"
    ).exclude(
        user_labels__name = "Oithona similis_paradinium"
    )
    
    print "got oithona queryset"
    """
    item = oith[0]
    
    ptf = os.path.join(in_path,str(item.id_to_path()), str(item.image_id))
    
    print "importing image and converting"    
    img = cv2.imread(ptf, cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, bayer_pattern)
    img = np.uint8(255*(np.float32(img) - np.min(img))/np.max(img))
    
    print "saving image"
    cv2.imwrite(os.path.join(out_path, str(item.image_id).split(".")[0]), img)
    print "done"
    """
    o_egg = Image.objects.filter(
        user_labels__name = "Oithona similis_egg sacs"
    )
    
    """
    o_par = Image.objects.filter(
        user_labels__name = "Oithona similis_paradinium"
    )
    """
    
    for item in oith:
        ptf = os.path.join(in_path,str(item.id_to_path()), str(item.image_id).split(".")[0]+".png")
        
        img = imread(ptf, IMREAD_UNCHANGED)
        
        imwrite(os.path.join(op1, str(item.image_id).split(".")[0]+".png"), img)
        
    print "done with oithona"
    
    for item in o_egg:
        ptf = os.path.join(in_path,str(item.id_to_path()), str(item.image_id).split(".")[0]+".png")
        
        img = imread(ptf, IMREAD_UNCHANGED)
        
        imwrite(os.path.join(op2, str(item.image_id).split(".")[0]+".png"), img)
        
    print "done with Oithona w/ eggs"
    
    """
    for item in o_par:
        ptf = os.path.join(in_path,str(item.id_to_path()), str(item.image_id).split(".")[0]+".png")
        
        img = imread(ptf, IMREAD_UNCHANGED)
        
        imwrite(os.path.join(op3, str(item.image_id).split(".")[0]+".png"), img)
    """    
    print "done"
