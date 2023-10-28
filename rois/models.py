from asyncio.proactor_events import _ProactorBaseWritePipeTransport
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from loguru import logger
import os
import errno
import datetime
import pytz
import rois.cvtools as cvtools
import shutil
import time
import json
import numpy as np
from loguru import logger

from rois.file_name_formats import FileNameFmt

""" A Description of ROI Processing Settings """
class ProcSettings(models.Model):
    
    # Name, desc and source for the settings
    name = models.CharField('Proc Settings Name',max_length=64,unique=True)
    description = models.CharField('Proc Settings Description',max_length=2048)
    source = models.CharField('Proc Settings Source Code',max_length=8192)
    
    # key parameters that all settings much implement and would be
    # desireable to search by
    
    # Preprecessing steps before detecting edges
    downsample_factor = models.IntegerField(
        'Downsample Factor',editable=False,db_index=True,default=2)
    channel_selector = models.IntegerField(
        'Channel Selector',editable=False,db_index=True,default=1)
    
    # Threshold used to define an edge
    edge_threshold_low = models.FloatField(
        'Edge Threshold Low',editable=False,db_index=True,default=1.0)
    edge_threshold_high = models.FloatField(
        'Edge Threshold High',editable=False,db_index=True,default=1.0)
    
    # Detector used to find edges
    edge_detector = models.CharField('Edge Detector',max_length=64)
    
    # Loaded from raw images
    load_raw = models.BooleanField(default=False)
    
    # How foreground objects are selected
    object_selection = models.CharField('Object Selection',max_length=64)
    
    # json data
    json_settings = {}
    
    def load_settings(self, filepath):
        try:
            self.json_settings = json.load(open(filepath))
        except:
            logger.error('Could not load settings file: ' + filepath)
            pass
        
        # populate DB fields
        self.source = json.dumps(self.json_settings)
        
        logger.debug(self.source)
        
        self.name = self.json_settings['name']
        self.description = self.json_settings['description']
        self.edge_threshold_high = self.json_settings['edge_threshold_high']
        self.edge_threshold_low = self.json_settings['edge_threshold_low']
        self.edge_detector = self.json_settings['edge_detector']
        self.object_selection = self.json_settings['object_selection']
        
    def load_default_settings(self):
        self.load_settings('default_proc_settings.json')

    def create(self):
        self.json_settings = json.loads(self.source)
        logger.debug(self.json_settings)
    
    def __str__(self):
        return self.name or ''

""" A Camera """
class Camera(models.Model):

    name = models.CharField('Camera Name',max_length=64,unique=True)
    description = models.CharField('Camera Description',max_length=2048)

""" A Taxanomic Label (ie copepod) """
class Label(MPTTModel):

    name = models.CharField('Label Name',max_length=512,primary_key=True)
    full_name = models.CharField(
            'Full Name',
            max_length=512,
            blank=True,
            unique=True
    )
    description = models.CharField('Label Description',max_length=2048)

    # Parent as a MPTT tree 
    parent = TreeForeignKey(
        'self',null=True,blank=True,related_name='children',on_delete=models.CASCADE)

    def __str__(self):
        return self.name or ''
    
    class MPTTMeta:
        order_insertion_by = ['name']

""" A General Tag (ie unique, or trained) """
class Tag(MPTTModel):

    name = models.CharField('Tag Name',max_length=64,primary_key=True)
    parent = TreeForeignKey(
        'self',null=True,blank=True,related_name='children',on_delete=models.CASCADE)

    def __str__(self):
        return self.name or ''
    
    class MPTTMeta:
        order_insertion_by = ['name']

""" A record of a query for images through the API """
class QueryRecord(models.Model):
    
    submitted = models.DateTimeField(
        'Submitted',editable=False,db_index=True)
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    path = models.CharField('Query Path',editable=False,max_length=2048)
    remote_addr = models.CharField(
        'Remote IP Address',editable=False,max_length=32,db_index=True,null=True,blank=True)
    user_agent = models.CharField(
        'User Agent',editable=False,max_length=2048,db_index=True,null=True,blank=True)

""" An Annotator """
class Annotator(models.Model):
    
    description = models.CharField('Annotator Description', null=True,
            blank=True, max_length=1024, default='')
    user = models.CharField('User name', max_length=1024, default='')

    name = models.CharField('Annotator name', max_length=1024, default='')
    
    def __str__(self):
        return self.name or ''

""" A Machine Annotator """
class MachineAnnotator(Annotator):

    timestamp = models.DateTimeField('Timestamp', editable=False,
            db_index=True)
    classifier_type = models.CharField('Classifier Type', null=True,
            blank=True, max_length=1024, default='')
            


""" A Human Annotator """
class HumanAnnotator(Annotator):
    pass

""" A set of labels and associated images """
class LabelSet(models.Model):

    name = models.CharField('Label Set Name',max_length=128,default='')
    started = models.DateTimeField(
        'Started',editable=False,db_index=True)
    submitted = models.DateTimeField(
        'Submitted',editable=False,db_index=True)
    label = models.ForeignKey(Label,related_name='label',on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    image_list = ArrayField(models.CharField(max_length=128),null=True)
    confidence_list = ArrayField(models.FloatField(),null=True)
    is_machine = models.BooleanField(default=False)
    user_info = models.TextField('User Info',null=True,blank=True,default='')
    machine_name = models.CharField('Machine Name',editable=False,max_length=1024,default='')
    notes = models.TextField('Notes',editable=True,null=True,blank=True,default='')
    query_path = models.CharField('Query Path',editable=False,null=True,blank=True,default='',max_length=2048)

    def total_images(self):
        return len(self.image_list)

    def total_time(self):
        return (self.submitted - self.started).seconds
    
    def images_per_second(self):
        if (self.submitted-self.started).seconds > 0:
            return float(len(self.image_list))/((self.submitted-self.started).seconds)
        else:
            return 0

""" A set of tags and associated images """
class TagSet(models.Model):

    started = models.DateTimeField(
        'Started',editable=False,db_index=True)
    submitted = models.DateTimeField(
        'Submitted',editable=False,db_index=True)
    tag = models.ForeignKey(Tag,related_name='tag',on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    image_list = ArrayField(models.CharField(max_length=128),null=True)
    confidence_list = ArrayField(models.FloatField(),null=True)
    is_machine = models.BooleanField(default=False)
    user_info = models.TextField('User Info',null=True,blank=True,default='')
    machine_name = models.CharField('Machine Name',editable=False,max_length=1024,default='')
    notes = models.TextField('Notes',editable=True,null=True,blank=True,default='')
    query_path = models.CharField('Query Path',editable=False,null=True,blank=True,default='',max_length=2048)
    def total_images(self):
        return len(self.image_list)

    def total_time(self):
        return (self.submitted - self.started).seconds
    
    def images_per_second(self):
        if (self.submitted-self.started).seconds > 0:
            return float(len(self.image_list))/((self.submitted-self.started).seconds)
        else:
            return 0



""" A image of a single object (ROI) """
class Image(models.Model):

    # Propteries of the extracted imaged
    timestamp = models.DateTimeField(
        'Timestamp',editable=False,db_index=True)
    major_axis_length = models.PositiveSmallIntegerField(
        'Major Axis Length',editable=False,db_index=True) 
    minor_axis_length = models.PositiveSmallIntegerField(
        'Minor Axis Length',editable=False,db_index=True)

    aspect_ratio = models.FloatField(
        'Aspect Ratio',editable=False,db_index=True,default=0.0)

    image_width = models.PositiveSmallIntegerField(
        'Image Width',editable=False,db_index=True,default=0)
    image_height = models.PositiveSmallIntegerField(
        'Image Height',editable=False,db_index=True,default=0)

    proc_time = models.PositiveSmallIntegerField(
        'Process Time',editable=False,db_index=True,default=0)
        
    proc_version = models.PositiveSmallIntegerField(
        'Process Version',editable=False,db_index=True,default=0)
    
    # Location information about the image, editable so it can be refined later
    # after inital image import
    latitude = models.FloatField(
        'Latitude',editable=True,db_index=True,default=0.0)
    
    longitude = models.FloatField(
        'Longitude',editable=True,db_index=True,default=0.0)
    
    depth = models.FloatField(
        'Depth',editable=True,db_index=True,default=0.0)
    
    # Aux sensor information acquired with the image
    temperature = models.FloatField(
        'Temperature',editable=True,db_index=True,default=0.0)
    
    salinity = models.FloatField(
        'Salinity',editable=True,db_index=True,default=0.0)
    
    chlorophyll = models.FloatField(
        'Chlorophyll',editable=True,db_index=True,default=0.0)
    
    # removed in favor of FFT-based sharpness estimate
    #blur_kernel_radius = models.PositiveSmallIntegerField(
    #    'Blur Kernel Radius',editable=False,db_index=True,default=1)
    
    sharpness = models.PositiveSmallIntegerField(
        'Sharpness',editable=False,db_index=True,default=0)

    # ID and file location information
    # All paths are derived from the image ID
    image_id = models.CharField(
        'Image ID',
        max_length=128,
        unique=True,
        db_index=True,
        editable=False,
        primary_key=True,
        default='')

    # Labels and tags
    
    user_labels = models.ManyToManyField(
        Label,related_name='example_image',blank=True)
    machine_labels = models.ManyToManyField(
        Label,related_name='machine_labeled_image',blank=True)
    tags = models.ManyToManyField(Tag,blank=True)

    

    # LabelSets and TagSets
    label_set = models.ManyToManyField(LabelSet,blank=True)
    tag_set = models.ManyToManyField(TagSet,blank=True)
    
    # The plankton camera that generated the roi
    camera = models.ForeignKey('Camera',null=True,on_delete=models.CASCADE)
    proc_settings = models.ForeignKey('ProcSettings',null=True,on_delete=models.CASCADE)

    # Flag to indicate the image may be clipped
    is_clipped = False


    # Meta information
    class Meta:
        ordering = ('-timestamp',)


    def get_camera(self):
        meta = self.explode_id()
        return Camera.objects.get(name=meta['camera'])

    # Check for a valid image id
    def valid_image_id(self):
        if (not self.explode_id()):
            print("Image ID is not valid.")
            return False
        return True

    # Map image_id to relative path
    def id_to_path(self):
        return Image.convert_to_path(self.image_id)
    
    # Map given image_id to relative path
    @staticmethod
    def convert_to_path(image_id):
        data = FileNameFmt.explode_filename(image_id)
        unixtime = data['unixtime']
        camera_dir = data['camera']
        
        outer_dir = str(int(unixtime/(86400)))
        inner_dir = str(int(unixtime/(864)))

        return os.path.join(camera_dir,outer_dir,inner_dir)

    # Create directory for image if it does not exist yet
    def create_dir_for_image(self,base_path='./'):

        # check for valid id
        if (not self.valid_image_id()):
            return False

        rel_path = self.id_to_path()
        try:
            os.makedirs(os.path.join(base_path,rel_path))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        return os.path.join(base_path,rel_path)

    def explode_id(self):

        #logger.debug(self.image_id)
        try:
            data = FileNameFmt.explode_filename(self.image_id)
        except:
            return False

        return data

    def get_image_path(self):
        return Image.convert_to_image_path(self.image_id)
    
    @staticmethod
    def convert_to_image_path(image_id):
        image_dir = os.path.join(
                settings.IMAGE_STORE,
                Image.convert_to_path(image_id)
        )
        image_path = os.path.join(
                image_dir,
                os.path.splitext(image_id)[0]
        )
        return image_path



    # return an html tag for the image
    def image_tag(self):
        full_path = self.get_image_path() + ".png"
        return u'<img src="%s" />' % full_path
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def full_image_path(self):
        return self.get_image_path() + ".png"
    
    # return an html tag for the image mask
    def binary_image_tag(self):
        full_path = self.get_image_path() + "_binary.png"
        return u'<img src="%s" />' % full_path
    binary_image_tag.short_description = 'Binary Image'
    binary_image_tag.allow_tags = True

    # return an html tag for the image boundary
    def boundary_image_tag(self):
        full_path = self.get_image_path() + "_boundary.png"
        return u'<img src="%s" />' % full_path
    boundary_image_tag.short_description = 'Boundary Image'
    boundary_image_tag.allow_tags = True
    
    # return an html tag for the image boundary
    def features_tag(self):
        full_path = self.get_image_path() + "_features.csv"
        return u'<a href="%s">Image Features</a>' % full_path
    features_tag.short_description = 'Image Features'
    features_tag.allow_tags = True
    
        
    # import and image from the local disk
    def import_image(self, path, proc_settings=None):
        
        # Load in the settings or a default
        if proc_settings is None:
            proc_settings = ProcSettings()
            proc_settings.load_default_settings()
            ps = ProcSettings.objects.filter(name = proc_settings.name)
            if not ps.exists():
                proc_settings.save()
            else:
                proc_settings = ps[0]

        self.proc_settings = proc_settings
        
        # check for valid id
        if (not self.valid_image_id()):
            return False

        # explode the image id into the image meta info
        image_meta = self.explode_id()

        # Create dir for the image if needed
        image_storage_path = self.create_dir_for_image(settings.IMAGE_STORE_FULL_PATH)
        
        # Create dir for backup if needed
        #backup_storage_path = self.create_dir_for_image(settings.BACKUP_IMAGE_PATH)
        
        proc_start_time = time.time()
        
        # Process the image and save the output
        img = np.array([])
        if self.image_id.split('.')[-1] == 'tif':
            # assume tif images are raw from the camera and need to be
            # converted
            if proc_settings.json_settings['is_raw']:
                img = cvtools.import_image(path,self.image_id.split('.tif')[0]+'_raw.tif', proc_settings.json_settings)
            else:
                img = cvtools.import_image(path,self.image_id, proc_settings.json_settings)
            #print "loading " + path + "/" + self.image_id + " ... "
            img_c_8bit = cvtools.convert_to_8bit(img, proc_settings.json_settings)
        else:
            # otherwise, png or jpg will just be read
            #print "loading " + path + "/" + self.image_id + " ... "
            img_c_8bit = cvtools.import_image(path,self.image_id, proc_settings.json_settings)
    
        output = cvtools.extract_features(
            img_c_8bit,
            img,
            proc_settings.json_settings, 
            save_to_disk=True,
            abs_path=image_storage_path,
            file_prefix=os.path.splitext(self.image_id)[0]
        )
        
        proc_end_time = time.time()

        #print("proc time: " + str(time.time()-proc_start_time))

        # Set the image features
        self.major_axis_length = output['features']['axis_major_length']
        self.minor_axis_length = output['features']['axis_minor_length']
        self.sharpness = output['sharpness']
        self.proc_time = proc_end_time - proc_start_time
        #self.proc_version = output['proc_version']
        
        if self.major_axis_length != 0:
            self.aspect_ratio = self.minor_axis_length/self.major_axis_length
        else:
            self.aspect_ratio = 1

        tz = pytz.timezone('UTC')
        self.timestamp = tz.localize(
                datetime.datetime.fromtimestamp(image_meta['unixtime'])
        )


        # Set the image width and height
        self.image_width = image_meta['image_width']
        self.image_height = image_meta['image_height']

        # print out the morpho stats with timestamp
        """
        if output['clipped_fraction'] <= 0.03 and settings.SAVE_MORPH:
            time_code = 7*24*3600*(int(image_meta['unixtime'])/(7*24*3600))
            morph_file = image_meta['camera']+'-'+str(time_code)+'-morph.csv'
            id_file = image_meta['camera']+'-'+str(time_code)+'-id.csv'
            morph_path = os.path.join(settings.MORPH_DIR,morph_file)
            id_path = os.path.join(settings.ID_DIR,id_file)
            morph_string = (str(self.timestamp)+','+
                    str(round(self.major_axis_length,3))+','+
                    str(round(self.minor_axis_length,3))+','+
                    str(round(self.aspect_ratio,3))+','+
                    str(round(self.sharpness,3))
                )
            print("saving morph data to " + morph_file)
            with open(morph_path,"a+") as mf:
                mf.write(morph_string+'\n')
            with open(id_path,"a+") as mf:
                mf.write(morph_string+','+self.image_id+'\n')
        """
        # Tag image as clipped if the clip fraction is more than 0.1
        if (output['clipped_fraction'] > 0.03):
            self.is_clipped = True
        
        # Set the camera
        if (Camera.objects.filter(name=image_meta['camera']).exists()):
            self.camera = Camera.objects.get(name=image_meta['camera'])
        else:
            c = Camera(name=image_meta['camera'])
            c.save()
            self.camera = c

        return True


""" Label Instance """
class LabelInstance(models.Model):

    image = models.ForeignKey(Image, related_name='labels',on_delete=models.CASCADE)
    label_set = models.ForeignKey(LabelSet, related_name='labels',on_delete=models.CASCADE)
    label = models.ForeignKey(Label, related_name='labels',on_delete=models.CASCADE)
    confidence = models.FloatField('Confidence Metric', editable=False,
            db_index=True, null=True, blank=True, default=None)
    created = models.DateTimeField('Created', editable=False, db_index=True)
    annotator = models.ForeignKey(Annotator, related_name='annotator',on_delete=models.CASCADE)

