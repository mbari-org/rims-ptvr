from rois.models import LabelSet, LabelInstance
from rois.models import HumanAnnotator, MachineAnnotator
from django.contrib.auth.models import User

def run(*args):

    # find all labelsets by given annotator
    


    for l in ls:
        lis = LabelInstance.objects.filter(label_set=l)
        for li in lis:
            li.annotator = ha
            li.save()
