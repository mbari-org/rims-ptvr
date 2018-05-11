from rois.models import Image, LabelSet, TagSet, Tag, Label, LabelInstance, HumanAnnotator
from django.contrib.auth.models import User
import glob
import os
import sys
import time
import datetime
import pytz

data_file = '/home/ptvradmin/virtualenvs/planktivore/planktivore_caymans/classes_1516combined.txt'

classes = [
    'empty',
    'fish_egg',
    'fish_larvae',
    'copepod_nauplius',
    'larvacean',
    'chaetognath',
    'diatom',
    'siphonophore',
    'jelly_other',
    'iso_amph_shrimp',
    'trichodesmium',
    'radiolarian',
    'echino_larvae',
    'pteropod',
    'rhizarian',
    'hard_to_id'
]

def run(*args):

    with open(data_file,"r") as f:
        
        # create the annotator for brian
        # see if human annotator exists
        if not HumanAnnotator.objects.filter(user='brian'):
            ha = HumanAnnotator(user='brian')
            ha.save()
        else:
            ha = HumanAnnotator.objects.filter(user='brian')[0]
        
        # create a new labelset for each class
        label_sets = []
        for c in classes:
            if c != 'empty':

                if not Label.objects.filter(pk=c):
                  label = Label(
                      name=c,
                      description=c,
                      full_name=c
                  )
                  label.save()
                else:
                  label = Label.objects.get(pk=c)
                
                if not LabelSet.objects.filter(name='brian_'+c):
                  ls = LabelSet()
                  ls.image_list = []
                  ls.confidence_list = []
                  ls.is_machine = False
                  ls.started = datetime.datetime.fromtimestamp(time.time(),tz=pytz.utc)
                  ls.submitted = datetime.datetime.fromtimestamp(time.time(),tz=pytz.utc)
                  ls.query_path = ''
                  ls.user = User.objects.get(username='brian')
                  ls.label = label
                  ls.save()
                else:
                  ls = LabelSet.objects.get(name='brian_'+c)
                  
                label_sets.append(ls)
        
        if not Tag.objects.filter(name='interesting_image'):
          interesting_tag = Tag(
              name = 'interesting_image',
          )
          interesting_tag.save()
        else:
          interesting_tag = Tag.objects.get(name='interesting_image')
        
        for line in f:
        
            print line
        
            tokens = line.split(' ')
            
            image_id = tokens[0]
            class_label = int(tokens[1])
            is_interesting = int(tokens[2])
            
            # add to label sets
            label_sets[int(class_label)-1].image_list.append(image_id)
            
            # get the image
            if not Image.objects.filter(pk=image_id):
              print 'missing ' + image_id
              continue
              
            img = Image.objects.get(pk=image_id)
            
            # create LabelInstance
            li = LabelInstance(
                annotator=ha,
                image=img,
                label=label_sets[int(class_label)-1].label,
                label_set = label_sets[int(class_label)-1],
                created = datetime.datetime.fromtimestamp(time.time(),tz=pytz.utc)
            )
            li.save()
            
            # add label and tag to image
            img.user_labels.clear()
            img.user_labels.add(label_sets[int(class_label)-1].label)
            if is_interesting == 1:
              img.tags.clear()
              img.tags.add(interesting_tag)
            img.save()
            
        # save the labelsets again
        for i in range(0,len(label_sets)):
            label_sets[i].save()


