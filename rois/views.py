from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from rois.models import Image, Tag, Label, LabelSet, TagSet, QueryRecord
from rois.models import Annotator, MachineAnnotator, HumanAnnotator, LabelInstance
from django.db.models import Q
from django.conf import settings
from rest_framework import viewsets, generics
from rois.serializers import ImageSerializer, ImageValueSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from utils import convert_date
import numpy as np
import json
import datetime
import time
import pytz
import os
import shutil
import sys
import subprocess

# Create your views here.
def browser(request):
    image_list = Image.objects.filter(image_id__contains='SPC-').filter(
            major_axis_length__range = [80,200]
    ).order_by('-image_height')[:200]
    template = loader.get_template('rois/browser.html')
    context = RequestContext(request, {
        'image_list': image_list,
    })
    return HttpResponse(template.render(context))

def totals(request,camera='SPC2'):
    resp = {}
    local_tz = pytz.timezone('America/Los_Angeles')
    dn = datetime.datetime.now(tz=local_tz)
    ds = datetime.datetime(dn.year,dn.month,dn.day,0,0,0,0,tzinfo=local_tz)
    resp['totals'] = Image.objects.filter(
            camera__name=camera,
            timestamp__range=[ds,dn]).count()
    return HttpResponse(json.dumps(resp),content_type="application/json")

def labels(request):
    resp = {}
    resp['labels'] = list(Label.objects.all().values())
    return HttpResponse(json.dumps(resp),content_type="application/json")
    
def annotators(request):
    resp = {}
    resp['annotators'] = list(Annotator.objects.all().values())
    return HttpResponse(json.dumps(resp),content_type="application/json")

def logout_user(request):
    if (request.is_ajax() and request.user.is_authenticated()):
        if request.method == 'POST':
            logout(request);
            return HttpResponse("OK")
    else:
        return HttpResponse("ERR")

#@csrf_exempt
def login_user(request):
    if (request.is_ajax()):
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                if user.is_active or user.is_superuser:
                    login(request,user)
                    return HttpResponse("OK")
                else:
                    return HttpResponse("ERR")
            else:
                return HttpResponse("INVALID 1")
        else:
            return HttpResponse("INVALID 2")
    else:
        return HttpResponse(str(request.META))
        #return HttpResponse("INVALID 3")

@ensure_csrf_cookie
def get_user(request):
    resp = {}
    resp['is_authenticated'] = request.user.is_authenticated()
    if (resp['is_authenticated']):
        resp['username'] = request.user.get_username()
    else:
        resp['username'] = 'Anonymous'
    return HttpResponse(json.dumps(resp),content_type="application/json")

def get_histograms(request):

    
    tday = datetime.date.today()
    start_hour = datetime.datetime(
            year=tday.year,
            month=tday.month,
            day=tday.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=pytz.UTC
    )
    

    # Extract the other settings from argumnts
    # assumes mm units for length
    min_length = float(0.2)/(7.38/1000)
    max_length = float(10.0)/(7.38/1000)
    length_inc = float(0.2)/(7.38/1000)
    min_aspect = float(0.0)
    max_aspect = float(1.0)
    aspect_inc = float(0.02)


    # Create ranges for histograms
    length_bins = np.arange(min_length,max_length,length_inc)
    aspect_bins = np.arange(min_aspect,max_aspect,aspect_inc)

    
    t1 = start_hour - datetime.timedelta(days=1)

    t2 = start_hour
    """
    tz = pytz.timezone('America/Los_Angeles')
    utcstart = self.kwargs['utcstart']
    utcend = self.kwargs['utcend']
    timestamp_start = datetime.datetime.fromtimestamp(int(utcstart)/1000,tz=pytz.utc)
    timestamp_end = datetime.datetime.fromtimestamp(int(utcend)/1000,tz=pytz.utc)
    
    # input from site is PST timezone. Compute offset to PDT if needed
    d1 = datetime.datetime.now(tz=pytz.utc)
    d2 = int(tz.normalize(d1).strftime('%s'))
    d1 = int(d1.strftime('%s'))
    hour_offset(d1-d2)/3600 - 8

    # pull other necessary parameters from url
    cam = self.kwargs['camera']
    hour_start = 0
    hour_end = 24 # for now just do full days (01/8/16 ECO)
    
    
    # build timestamp query object over all days
    n_days = (timestamp_end-timestamp_start).days
    time_query = Q()
    for d in range(0,n_days):
        day_s = timestamp_start + datetime.timedelta(
                days=d,
                hours=int(hour_start) + hour_offset
                )
        day_e = timestamp_end + datetime.timedelta(
                days=d,
                hours=int(hour_end) + hour_offset
                )
        time_query = time_query | Q(timestamp__range=[day_s,day_e])
    
    """
    # retrive queryset
    
    values_list = Image.objects.filter(timestamp__gte=t1,
            timestamp__lt=t2,
            camera__name=cam).values_list('major_axis_length',
            'aspect_ratio')
    """

    values_list = Image.objects.filter(time_query,
            camera__name=cam).values_list('major_axis_length',
                    'aspect_ratio')
    """
    # Process
    major_lengths = np.array(values_list)[:,0]
    aspect_ratios = np.array(values_list)[:,1]
    total_rois = major_lengths.size
    

    # Compute histograms
    length_bins = (length_bins*7.38/1000.0).tolist()
    aspect_bins = aspect_bins.tolist()
    length_counts = np.histogram(major_lengths*7.38/1000.0,length_bins)
    aspect_counts = np.histogram(aspect_ratios,aspect_bins)

    length_counts = length_counts[0].tolist()
    aspect_counts = aspect_counts[0].tolist()
    
    resp = {}
    resp['datasets'] = []
    dataset = {}
    dataset['data'] = length_counts
    dataset['name'] = 'Length Counts'
    dataset['unit'] = 'Counts'
    dataset['type'] = 'line'
    dataset['valueDecimals'] = 1
    resp['datasets'] = [dataset]
    resp['xData'] = length_bins
    
    return HttpResponse(json.dumps(resp),content_type="application/json")


@csrf_exempt
def label_images(request):

    if (request.is_ajax() and request.user.is_authenticated()):
        if request.method == 'POST':
            #print ('Raw Data:',request.body)

            data = json.loads(request.body)

            label_name = data['label']
            if 'machine_name' in data:
                machine_name = data['machine_name']
            else:
                machine_name = ''
            tag_name = data['tag']
            started = data['started']
            submitted = data['submitted']
            
            if 'name' in data:
                labelset_name = data['name']
            else:
                labelset_name = ''
    
            if 'notes' in data:
                notes = data['notes']
            else:
                notes = ''

            if 'is_machine' in data:
                is_machine = data['is_machine']
            else:
                is_machine = False

            if 'confidence_list' in data:
                confidence_list = data['confidence_list']
            else:
                confidence_list = []

            if 'query_path' in data:
                query_path = data['query_path']
            else:
                query_path = ''

            if 'user_info' in data:
                user_info = data['user_info']
            else:
                user_info = ''

            # check for some valid label or tag
            if (label_name == 'None' and tag_name == 'None'):
                return HttpResponse("NO ACTION")

            # Get the images to update
            if 'images' in data:
                imgs = Image.objects.filter(pk__in=data['images'])
            
            if 'image_ids' in data:
                imgs= Image.objects.filter(image_id__in=data['image_ids'])

            # keep track of what images were labeled/tagged
            labeled_images = []
            tagged_images = []

            # Add the labels if not equal to none
            # and create a new labels set
            if (label_name != ''):
                label = Label.objects.filter(pk=label_name)
                if (not label.exists()):
                    label = Label(
                        name=label_name,
                        description=label_name,
                        full_name=label_name
                    )
                    label.save()
                else:
                    label = label[0]

                # loop through images and add label
                for img in imgs:
                    img.user_labels.add(label)
                    img.save()
                    labeled_images = labeled_images + [img.pk]
                
                # create new label set
                ls = LabelSet()
                ls.image_list = labeled_images
                ls.confidence_list = confidence_list
                #if machine_name:
                ls.machine_name = machine_name
                ls.is_machine = is_machine
                #else:
                #    ls.machine_name = ''
                #    ls.is_machine = False

                ls.user_info = user_info
                ls.query_path = query_path
                ls.user = request.user
                ls.label = label
                ls.submitted = datetime.datetime.fromtimestamp(
                        int(submitted)/1000,tz=pytz.utc
                )
                ls.started = datetime.datetime.fromtimestamp(
                        int(started)/1000,tz=pytz.utc
                )
                ls.save()
                
                # check if the annotator is a machine
                if is_machine:

                    # see if the annotator object exists
                    if not MachineAnnotator.objects.filter(name=machine_name):
                        ma = MachineAnnotator(user=request.user.get_username(),
                                name=machine_name,
                                timestamp=ls.started)
                        ma.save()
                    else:
                        ma = MachineAnnotator.objects.filter(name=machine_name)[0]

                    # include confidence list in label instance if it exists
                    if confidence_list:
                        for img, conf in zip(imgs, confidence_list):
                            labint = LabelInstance(image=img,
                                    label=label,
                                    label_set=ls,
                                    confidence=conf,
                                    created=ls.started,
                                    annotator=ma)
                            labint.save()
                    else:
                        for img in imgs:
                            labint = LabelInstance(image=img,
                                    label=label,
                                    label_set=ls,
                                    created=ls.started,
                                    annotator=ma)
                            labint.save()
                else:

                    # see if human annotator exists
                    if not HumanAnnotator.objects.filter(user=request.user.get_username()):
                        ha = HumanAnnotator(user=request.user.get_username(),name=request.user.get_username())
                        ha.save()
                    else:
                        ha = HumanAnnotator.objects.filter(user=request.user.get_username())[0]

                    # go through the images and create the label instances
                    for img in imgs:
                        labint = LabelInstance(image=img,
                                label_set=ls,
                                label=label,
                                created=ls.started,
                                annotator=ha)
                        labint.save()

            # Add the tags if not equal to none
            if (tag_name != ''):
                tag_tokens = tag_name.split(',')
                for tag_item in tag_tokens:
                    tagged_images = []
                    tag = Tag.objects.filter(pk=tag_item)
                    if (not tag.exists()):
                        tag = Tag(
                            name=tag_item
                            #description=tag_name,
                            #full_name=tag_name
                        )
                        tag.save()
                    else:
                        tag = tag[0]
                    for img in imgs:
                        img.tags.add(tag)
                        img.save()
                        tagged_images = tagged_images + [img.pk]
                    # create new tag set
                    ts = TagSet()
                    ts.image_list = tagged_images
                    ts.confidence_list = confidence_list
                    #if machine_name:
                    ts.machine_name = machine_name
                    ts.is_machine = False
                    #else:
                    #    ts.machine_name = ''
                    #    ts.is_machine = False

                    ts.user_info = user_info
                    ts.query_path = query_path
                    ts.user = request.user
                    ts.tag = tag
                    ts.submitted = datetime.datetime.fromtimestamp(
                            int(submitted)/1000,tz=pytz.utc
                    )
                    ts.started = datetime.datetime.fromtimestamp(
                            int(started)/1000,tz=pytz.utc
                    )
                    ts.save()

            resp = {}
            resp['labeled_images'] = labeled_images
            resp['tagged_images'] = tagged_images
            return HttpResponse(json.dumps(resp),content_type="application/json")
    else:
        return HttpResponse("Not Logged In.")

def tags(request):
    resp = {}
    resp['tags'] = list(Tag.objects.all().values())
    return HttpResponse(json.dumps(resp),content_type="application/json")


def find_image(request,image_id=''):
   
    # Force .tif ending of id
    l = image_id.split('.')
    image_id = l[0] + '.tif'

    obj = Image.objects.filter(
        image_id=image_id
    )
    if (obj.count() > 0):
        return HttpResponse(
            JSONRenderer().render(ImageSerializer(obj[0]).data),
            content_type="application/json"
        )
    else:
        resp = {}
        resp['image_id'] = ''
        return HttpResponse(json.dumps(resp),content_type="application/json")

class ImageViewSet(viewsets.ModelViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get_queryset(self):

        cam = self.kwargs['camera']
        return self.queryset.filter(camera__name=cam)


class ImageListPagination(PageNumberPagination):
    page_size = 500
    max_page_size = 50000
        
class ImageList(generics.ListAPIView):

    serializer_class = ImageSerializer
    pagination_class = ImageListPagination

    queryset = []

    def get(self,request,*args,**kwargs):
        self.pagination_class.page_size = self.kwargs['nimages']
        response = super(ImageList,self).get(request,*args,**kwargs)
        if len(response.data) == 0:
            response.data = [{}]
        #response.data = {}
        r = response.data
        response.data = {}
        response.data['archive_url'] = self.archive_url
        response.data['image_data'] = r
        response.data['total_matching'] = self.total_matching
        response.data['query_time'] = self.query_time
        response.data['page_size'] = self.kwargs['nimages']
        #response.data['page_size'] = settings.REST_FRAMEWORK['PAGE_SIZE']  


        # sort the result by image height
        #response.data['image_data']['results'] = sorted(response.data['image_data']['results'],key=lambda o:-o.image_height)

        # Create a record of the request
        qr = QueryRecord()
        qr.path = request.path
        qr.user_agent = request.META['HTTP_USER_AGENT']
        qr.remote_addr = request.META['HTTP_X_REAL_IP']
        qr.submitted = datetime.datetime.now(tz=pytz.utc)
        if (request.user.is_authenticated()):
            qr.user = request.user
        qr.save()
       

        return response

    def get_queryset(self):

        if len(self.queryset) != 0:
            return self.queryset

        cam = self.kwargs['camera']
        utcstart = self.kwargs['utcstart']
        utcend = self.kwargs['utcend']
        tz = pytz.timezone('America/Los_Angeles')

        """ 
        #timestamp_start = tz.normalize(timestamp_start)
        #timestamp_end = tz.normalize(timestamp_end)

        # input to the API is from PST timezone so convert to PDT
        # if needed
        d1 = datetime.datetime.now(tz=pytz.utc)
        d2 = int(tz.normalize(d1).strftime('%s'))
        d1 = int(d1.strftime('%s'))
        hour_offset = (d1-d2) - 8*3600
        #hour_offset = 0
        
        timestamp_start = datetime.datetime.fromtimestamp(int(utcstart)/1000 + hour_offset,tz=pytz.utc)
        timestamp_end = datetime.datetime.fromtimestamp(int(utcend)/1000 + hour_offset,tz=pytz.utc)
        """
        timestamp_start = convert_date(utcstart)
        timestamp_end = convert_date(utcend)

        nimages = self.kwargs['nimages']
        minlen = self.kwargs['minlen']
        maxlen = self.kwargs['maxlen']
        minaspect = self.kwargs['minaspect']
        maxaspect = self.kwargs['maxaspect']
        exclude = self.kwargs['exclude']
        ordering = self.kwargs['ordering']
        do_archive = self.kwargs['archive']
        hour_start = self.kwargs['hourstart']
        hour_end = self.kwargs['hourend']
        label_name = self.kwargs['label']
        tag_name = self.kwargs['tag']
        annotator_name = self.kwargs['annotator']
        self.total_count = 100
        
        noclipped = exclude.find('clipped') != -1 
        randomize = ordering.find('randomize') != -1 

        # build the timestamp query object over all days
        #n_days = (timestamp_end-timestamp_start).days
        #time_query = Q()
        #if int(hour_end) - int(hour_start) != 24:
        #    for d in range(0,n_days):
        #        day_s = timestamp_start + datetime.timedelta(
        #                days=d,
        #                hours=int(hour_start) + hour_offset
        #        )
        #        day_e = timestamp_start + datetime.timedelta(
        #                days=d,hours=int(hour_end) + hour_offset
        #        )
        #        time_query = time_query | Q(timestamp__range=[day_s,day_e])
        #else:
        time_query = Q(timestamp__range=[timestamp_start,timestamp_end])

        qs = Image.objects.filter(
                time_query,
                camera__name=cam,
                #timestamp__range = [timestamp_start,timestamp_end],
                #timestamp__hour = hour_start,
                major_axis_length__range = [minlen,maxlen],
                aspect_ratio__range = [minaspect,maxaspect],
        ).prefetch_related('tags','user_labels')
        #)
      
        # Possibly exclude clipped images
        if (noclipped):
            qs = qs.exclude(tags__pk='Clipped Image')
        
        ## Filter on label if requested
        #if (label_name.lower() == 'unlabeled'):
        #    qs = qs.filter(user_labels__isnull=True)
        #elif (label_name.lower() != 'any'):
        #    qs = qs.filter(user_labels__name=label_name)
        #    if (self.kwargs['labeltype'] == 'machines'):
        #        machine_labels = LabelSet.objects.filter(
        #                label__name=label_name,
        #                is_machine=True
        #        ).values_list('image_list')
        #        machine_labels_ids = sum(machine_labels,())
        #        qs = qs.filter(pk__in = machine_labels_ids[0])
        #    elif (self.kwargs['labeltype'] == 'humans'):
        #        human_labels = LabelSet.objects.filter(
        #                label__name=label_name,
        #                is_machine=False
        #        ).values_list('image_list')
        #        human_labels_ids = sum(human_labels,())
        #        qs = qs.filter(pk__in = human_labels_ids[0])

        # Filter on label if requestedi

        lqs = LabelInstance.objects

        # check for invert selector
        invert_labels = False
        if len(label_name) > 1:
            if label_name[0] == '!':
                label_name = label_name[1:]
                invert_labels = True
        
        if invert_labels:
        
            if (label_name.lower() == 'unlabeled'):
                qs = qs.filter(user_labels__isnull=False)
            elif (label_name.lower() != 'any'):
                if (self.kwargs['labeltype'] == 'machines'):
                    lqs = lqs.exclude(
                            label__name__in=label_name.split(','),
                            annotator__in=MachineAnnotator.objects.all()
                        )
                elif (self.kwargs['labeltype'] == 'humans'):
                    lqs = lqs.exclude(
                            label__name__in=label_name.split(','),
                            annotator__in=HumanAnnotator.objects.all()
                        )
                else:
                    lqs = lqs.exclude(label__name__in=label_name.split(','))

        else:

            if (label_name.lower() == 'unlabeled'):
                qs = qs.filter(user_labels__isnull=True)
            elif (label_name.lower() != 'any'):
                if (self.kwargs['labeltype'] == 'machines'):
                    lqs = lqs.filter(
                            label__name__in=label_name.split(','),
                            annotator__in=MachineAnnotator.objects.all()
                        )
                elif (self.kwargs['labeltype'] == 'humans'):
                    lqs = lqs.filter(
                            label__name__in=label_name.split(','),
                            annotator__in=HumanAnnotator.objects.all()
                        )
                else:
                    lqs = lqs.filter(label__name__in=label_name.split(','))


        # Filter on tag if requested
        if (tag_name.lower() == 'untagged'):
            qs = qs.filter(tags__isnull=True)
        elif (tag_name.lower() != 'any'):
            qs = qs.filter(tags__pk=tag_name)
            
        # Filter on tag if requested
        if (annotator_name.lower() != 'any'):
            lqs = lqs.filter(
                    annotator__name__in=annotator_name.split(',')
            )
            #qs = qs.filter(pk__in = image_ids)


        # apply the label and annotator filters
        qs = qs.filter(pk__in = lqs.values_list('image__image_id'))


        # if not archving, get a subset of the total
        ts = time.time()
        #if do_archive.find('archive') == -1:
        #if (randomize):
        #    qs = qs.order_by('?')[0:nimages]
        #else:
        #    qs = qs.order_by('-timestamp')[0:nimages]
        
        if (randomize):
            qs = qs.order_by('?')
        else:
            qs = qs.order_by('-timestamp')
        #qs = qs.values()
        #qs = qs.order_by('-image_height')

        #ql = list(qs)
        #te = time.time()
        #self.query_time = (te-ts)*1000
        #self.total_matching = ql.__len__()

        self.query_time = 0
        self.total_matching = nimages

        # uncomment to log query string
        #print >>sys.stderr, str(qs.query)


        # copy images and records to temp place
        archive_name = (cam +  
            '-' + str(int(utcstart)/1000) + 
            '-' + str(int(utcend)/1000) + 
            '-' + nimages + 
            '-' + minlen + 
            '-' + maxlen +
            '-' + minaspect + 
            '-' + maxaspect +
            '-' + exclude + 
            '-' + ordering + 
            '-' + hour_start + 
            '-' + hour_end + 
            '-' + label_name + 
            '-' + tag_name
        )

        self.archive_url = ''

        if False:
        #if do_archive.find('archive') != -1:
            # make archive dir and copy images to it
            archive_dir = os.path.join(settings.TMP_ARCHIVE_ROOT,archive_name)
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)

            for image in ql:
                image_path = ('/home/spcadmin/virtualenvs/planktonview2' +
                        image.get_image_path() + '.png'
                )
                shutil.copy(image_path,archive_dir)

            serializer = ImageSerializer(qs,many=True)

            with open(os.path.join(archive_dir,'db_output.json'),'w') as outfile:
                json.dump(serializer.data,outfile,sort_keys=True,indent=4)

            subprocess.call(['zip','-r9FSj',archive_dir+'.zip',archive_dir])

            self.archive_url = os.path.join(settings.TMP_ARCHIVE_URL,archive_name+'.zip')   
        
        # return the results sorted by image height for display 
        #return sorted(qs,key=lambda o:-o.image_height)
        return qs

class ImageArchive(generics.ListAPIView):

    serializer_class = ImageValueSerializer

    queryset = Image.objects.all()

    def get(self,request,*args,**kwargs):
        response = super(ImageArchive,self).get(request,*args,**kwargs)
        if len(response.data) == 0:
            response.data = [{}]
        #response.data = {}
        r = response.data
        response.data = {}
        response.data['archive_url'] = self.archive_url
        response.data['image_data'] = r
        response.data['total_matching'] = self.total_matching
        response.data['query_time'] = self.query_time
       


        # Create a record of the request
        qr = QueryRecord()
        qr.path = request.path
        qr.user_agent = request.META['HTTP_USER_AGENT']
        qr.remote_addr = request.META['HTTP_X_REAL_IP']
        qr.submitted = datetime.datetime.now(tz=pytz.utc)
        if (request.user.is_authenticated()):
            qr.user = request.user
        qr.save()
       

        return response

    def get_queryset(self):

        cam = self.kwargs['camera']
        utcstart = self.kwargs['utcstart']
        utcend = self.kwargs['utcend']
        tz = pytz.timezone('America/Los_Angeles')
        #timestamp_start = datetime.datetime.fromtimestamp(int(utcstart)/1000,tz=pytz.utc)
        #timestamp_end = datetime.datetime.fromtimestamp(int(utcend)/1000,tz=pytz.utc)
        timestamp_start = convert_date(utcstart)
        timestamp_end = convert_date(utcend)
        

        #timestamp_start = tz.normalize(timestamp_start)
        #timestamp_end = tz.normalize(timestamp_end)



        # input to the API is from PST timezone so convert to PDT
        # if needed
        d1 = datetime.datetime.now(tz=pytz.utc)
        d2 = int(tz.normalize(d1).strftime('%s'))
        d1 = int(d1.strftime('%s'))
        hour_offset = (d1-d2)/3600 - 8
        #hour_offset = 0

        minlen = self.kwargs['minlen']
        maxlen = self.kwargs['maxlen']
        minaspect = self.kwargs['minaspect']
        maxaspect = self.kwargs['maxaspect']
        exclude = self.kwargs['exclude']
        hour_start = self.kwargs['hourstart']
        hour_end = self.kwargs['hourend']
        label_name = self.kwargs['label']
        tag_name = self.kwargs['tag']
        self.total_count = 100
        
        noclipped = exclude.find('clipped') != -1 
        
        # copy images and records to temp place
        archive_name = (cam +  
            '-' + str(int(utcstart)/1000) + 
            '-' + str(int(utcend)/1000) + 
            '-' + hour_start + 
            '-' + hour_end + 
            '-' + minlen + 
            '-' + maxlen +
            '-' + minaspect + 
            '-' + maxaspect +
            '-' + exclude + 
            '-' + label_name + 
            '-' + tag_name
        )

        archive_dir = os.path.join(settings.TMP_ARCHIVE_ROOT,archive_name)
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
       
        log_file = os.path.join(settings.TMP_ARCHIVE_ROOT,archive_name+'.json')

        log = []
        log.append('starting archive process...')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
        
        # build the timestamp query object over all days
        #n_days = (timestamp_end-timestamp_start).days
        #time_query = Q()
        #if int(hour_end)-int(hour_start) != 24:
        #    for d in range(0,n_days):
        #        day_s = timestamp_start + datetime.timedelta(
        #                days=d,
        #                hours=int(hour_start) + hour_offset
        #        )   
        #        day_e = timestamp_start + datetime.timedelta(
        #                days=d,hours=int(hour_end) + hour_offset
        #        )
        #        time_query = time_query | Q(timestamp__range=[day_s,day_e])
#
        #else:
        time_query = Q(timestamp__range=[timestamp_start,timestamp_end])

        qs = self.queryset.filter(
                time_query,
                camera__name=cam,
                #timestamp__range = [timestamp_start,timestamp_end],
                #timestamp__hour = hour_start,
                major_axis_length__range = [minlen,maxlen],
                aspect_ratio__range = [minaspect,maxaspect],
        ).prefetch_related('tags','user_labels')
        #)
        
        # Possibly exclude clipped images
        if (noclipped):
            qs = qs.exclude(tags__pk='Clipped Image')
        
        # Filter on label if requested
        if (label_name.lower() == 'unlabeled'):
            qs = qs.filter(user_labels__isnull=True)
        elif (label_name.lower() != 'any'):
            qs = qs.filter(user_labels__name=label_name)

        # Filter on tag if requested
        if (tag_name.lower() == 'untagged'):
            qs = qs.filter(tags__isnull=True)
        elif (tag_name.lower() != 'any'):
            qs = qs.filter(tags__pk=tag_name)

        
        log.append('running query...')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)

        # if not archving, get a subset of the total
        ts = time.time()
        
        qs = qs.values()

        ql = list(qs)
        te = time.time()
        self.query_time = (te-ts)*1000
        self.total_matching = ql.__len__()

        log.append('completed query.')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
        
        
        self.archive_url = ''

        log.append('collecting ' + str(len(ql)) + ' files....')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
       
        counter = 0

        for image in ql:
            image_path = ('/home/spcadmin/virtualenvs/planktonview2' +
                    Image.convert_to_image_path(image['image_id']) + '.png'
            )
            shutil.copy(image_path,archive_dir)
            counter = counter + 1
            if counter % 100 == 0:
                log[-1] = 'collected ' + str(counter) + ' of ' + str(len(ql)) + ' files...'
                with open(log_file,'w') as outfile:
                    json.dump(log,outfile,sort_keys=True,indent=4)


        log.append('serializing database entries....')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
        serializer = ImageValueSerializer(qs,many=True)

        with open(os.path.join(archive_dir,'db_output.json'),'w') as outfile:
            json.dump(serializer.data,outfile,sort_keys=True,indent=4)

        log.append('bundling archive file....')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
        subprocess.call(['zip','-r9FSj',archive_dir+'.zip',archive_dir])

        log.append('Done.')
        with open(log_file,'w') as outfile:
            json.dump(log,outfile,sort_keys=True,indent=4)
        self.archive_url = os.path.join(settings.TMP_ARCHIVE_URL,archive_name+'.zip')   
        return []

