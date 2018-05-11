from rest_framework import serializers
from roistats.models import DailyStats, HourlyStats

class DailyStatsSerializer(serializers.HyperlinkedModelSerializer):

    #api_url = serializers.SerializerMethodField('get_api_url')
    camera_name = serializers.SerializerMethodField()

    class Meta:

        model = DailyStats
        fields = (
                'day',
                'camera_name', 
                'total_rois',
        )

    def get_camera_name(self,obj):
        return obj.camera.name

class HourlyStatsSerializer(serializers.HyperlinkedModelSerializer):

    #api_url = serializers.SerializerMethodField('get_api_url')
    camera_name = serializers.SerializerMethodField()

    class Meta:

        model = HourlyStats
        fields = (
                'hour',
                'camera_name', 
                'total_rois',
                'average_major_length',
                'stddev_major_length',
                'average_minor_length',
                'stddev_minor_length'
        )

    def get_camera_name(self,obj):
        return obj.camera.name
