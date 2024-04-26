from rest_framework import serializers
from rois.models import Image, Camera
import pytz

#class CameraSerializer(serializers.HyperlinkedModelSerializer):
#
#    class Meta:
#
#        model = Camera
#        fields = ('name','description')


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    #api_url = serializers.SerializerMethodField('get_api_url')
    image_url = serializers.SerializerMethodField()
    image_timestamp = serializers.SerializerMethodField()
    #camera_name = serializers.SerializerMethodField()
    #tag_name = serializers.SerializerMethodField()
    #user_labels = serializers.StringRelatedField(many=True)
    user_labels = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:

        model = Image
        #fields = ('user_labels', 'machine_labels', 'tags',
        #    'id', 'image_id', 'major_axis_length',
        #    'minor_axis_length','image_width','image_height',
        #    'camera_name','image_url'
        #)
        fields = ('image_timestamp','major_axis_length',
                'minor_axis_length','aspect_ratio','image_url',
                'image_width','image_id','image_height','depth', 
                'temperature', 'chlorophyll', 'latitude', 'longitude', 'user_labels','tags',
        )

    #def get_api_url(self,obj):
    #    return "#/image/%s" % obj.id

    def get_user_labels(self,obj):

        output = []

        for l in obj.labels.all():
            output.append(l.label.name)

        return output

    def get_image_url(self,obj):
        return obj.get_image_path()

    def get_image_timestamp(self,obj):
        tz = pytz.timezone('America/Los_Angeles')
        return  obj.timestamp.strftime('%c %Z')

    def get_camera_name(self,obj):
        return obj.camera.name
    def get_tag_name(self,obj):
        output = ''
        for tag in obj.tags.all():
            output = tag.name + ", " + output

        return output

class ImageValueSerializer(serializers.HyperlinkedModelSerializer):

    #api_url = serializers.SerializerMethodField('get_api_url')
    #image_url = serializers.SerializerMethodField()
    #image_timestamp = serializers.SerializerMethodField()
    #camera_name = serializers.SerializerMethodField()
    #tag_name = serializers.SerializerMethodField()
    #user_labels = serializers.StringRelatedField(many=True)
    #tags = serializers.StringRelatedField(many=True)

    class Meta:

        model = Image
        #fields = ('user_labels', 'machine_labels', 'tags',
        #    'id', 'image_id', 'major_axis_length',
        #    'minor_axis_length','image_width','image_height',
        #    'camera_name','image_url'
        #)
        fields = ('major_axis_length',
                'minor_axis_length','aspect_ratio',
                'image_width','image_id','image_height','timestamp',
        )

    #def get_api_url(self,obj):
    #    return "#/image/%s" % obj.id
    
