from rois.models import Annotator, HumanAnnotator, MachineAnnotator, LabelSet, Image, LabelInstance
import datetime
import pytz

def run():
    # get a recent LabelSet and print out some of the info
    labset = LabelSet.objects.filter(is_machine=True)[50]

    # display some info
    print "User name: " + str(labset.user)
    print "Number of images: " + str(labset.total_images())
    print "Label: " + str(labset.label)
    print "machine name: " + labset.machine_name
    print "started: " + str(type(labset.started))

    # create a machine annotator
    ma = MachineAnnotator(timestamp = labset.started, classifier_type
            = "SVM", name = labset.machine_name, user=labset.user_info)

    # save into db
    ma.save()
    
    # Get some machine annotator info
    qs = MachineAnnotator.objects.all()
    print qs.values_list()

    # print some info
    print "Type of MachineAnnotator: " + str(type(ma))

    print "Is object a MachineAnnotator: " + str(isinstance(ma,
        MachineAnnotator))

    # get some type information
    print "Type of image_list entry: " + str(type(labset.image_list[0]))
    print "Type of labset: " + str(type(labset))
    print "Type of confidence: " + str(type(labset.confidence_list[0]))
    
    # get the image object
    im = Image.objects.filter(pk=labset.image_list[0])
    
    # play around with LabelInstances
    labint = LabelInstance(image=im[0], label_set = labset,
            label = labset.label, confidence=labset.confidence_list[0],
            created=labset.started, annotator=ma)
    labint.save()

    # get some label instance info
    qs = LabelInstance.objects.all()
    print qs.values_list()

    # delete the test machine annotator object
    ma.delete()

    # delete LabelInstance object
    labint.delete()
    
    # make a human annototor
    labset = LabelSet.objects.filter(is_machine=False)[0]
    ha = HumanAnnotator(user=labset.user_info)
    ha.save()

    qh = HumanAnnotator.objects.all()
    print qh.values_list()

    print Annotator.objects.all()

    # create a human annotator label istance
    im = Image.objects.filter(pk=labset.image_list[0])
    haint = LabelInstance(image=im[0], label_set=labset,
            label = labset.label, created=labset.started, annotator=ha)

    haint.save()

    qs = LabelInstance.objects.all()
    print qs.values_list()

    # delete the human annotator
    ha.delete()

    haint.delete()
    # check that it is gone
    print Annotator.objects.all()
    print MachineAnnotator.objects.all()
    print LabelInstance.objects.all()
