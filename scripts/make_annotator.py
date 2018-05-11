from rois.models import Annotator, HumanAnnotator, MachineAnnotator, LabelSet, Image, LabelInstance

"""
Created Mon Apr 16, 2018

Creates Annotator and LabelInstance objects from all existing labelsets

@author: Eric Orenstein
"""
def run():

    # read in label sets
    labset = LabelSet.objects.all()
    # print str(labset.count())
    flag = 0    
    # loop through and create annotators
    for item in labset:

        # check if it is machine
        if not item.is_machine:
            # check if a human record exists and create the object if needed
            if not HumanAnnotator.objects.filter(user=item.user_info):
                ha = HumanAnnotator(user=item.user_info)
                ha.save()
            else:
                ha = HumanAnnotator.objects.filter(user=item.user_info)[0]
            
            # Loop over images and add lab instances
            for im in item.image_list:
                try:
                    img = Image.objects.filter(pk=im)[0]
                    labint = LabelInstance(image=img, label_set=item, 
                            label=item.label, created=item.started, annotator=ha)
                    labint.save()
                except IndexError:
                    print "Skipping " + str(im) + ". Object not found"
        else:
            # check if an associated machine object exists and create if needed
            if not MachineAnnotator.objects.filter(name=item.machine_name):
                ma = MachineAnnotator(user=item.user_info, name=item.machine_name,
                        timestamp=item.started)
                ma.save()
            else:
                ma = MachineAnnotator.objects.filter(name=item.machine_name)[0]

            # loop over the image list and create the label instance object
            # Check if the label set has a confindence list
            
            if not item.confidence_list:
                # if no confidence list, just add image pk
                try:
                    for im in item.image_list:
                        img = Image.objects.filter(pk=im)[0]
                        labint = LabelInstance(image=img, label_set=item,
                                label=item.label, created=item.started, annotator=ma)
                        labint.save()
                except IndexError:
                    print "Skipping " + str(im) + ". Object not found"
            else:
                # otherwise add the confidence metric
                try:
                    for im, conf in zip(item.image_list, item.confidence_list):
                        img = Image.objects.filter(pk=im)[0]
                        labint = LabelInstance(image=img, label_set=item,
                                label=item.label, confidence=conf,
                                created=item.started, annotator=ma)
                        labint.save()
                except IndexError:
                    print "Skipping " + str(im) + ". Object not found"

        # say where you are
        flag += 1
        print "done with " + str(flag) + " of " + str(labset.count())

    print "object creation complete"
    qs = LabelInstance.objects.all()
    print "Total label instances: " + str(qs.count())
    qs = Annotator.objects.all()
    print "Total annotators: " + str(qs.count())
    qs = HumanAnnotator.objects.all()
    print "Total human annotators: " + str(qs.count())
    qs = MachineAnnotator.objects.all()
    print "Total machine annotators: " + str(qs.count())
    """
    qh = Annotator.objects.all()
    print qh.values_list()
    qh = MachineAnnotator.objects.all()
    print qh.values_list()
    qh.delete()
    """
