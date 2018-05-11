from rest_framework import serializers
from systemstats.models import MinuteStats

class MinuteStatsSerializer(serializers.HyperlinkedModelSerializer):

    #api_url = serializers.SerializerMethodField('get_api_url')
    camera_name = serializers.SerializerMethodField()

    class Meta:

        model = MinuteStats
        fields = (
                'timestamp',
                'camera_name', 
                'counts',
        )

    def get_camera_name(self,obj):
        return obj.camera.name
