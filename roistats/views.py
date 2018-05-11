from django.http import HttpResponse
from django.template import RequestContext, loader
from roistats.models import DailyStats, HourlyStats
from rest_framework import viewsets, generics, pagination
from roistats.serializers import DailyStatsSerializer, HourlyStatsSerializer
import datetime
import pytz

# Create your views here.

class DailyPagination(pagination.PageNumberPagination):
    page_size = 3000

class DailyStatsList(generics.ListAPIView):

    serializer_class = DailyStatsSerializer

    queryset = DailyStats.objects.all()

    pagination_class = DailyPagination
    
    
    def get_queryset(self):

        cam = self.kwargs['camera']
        return self.queryset.filter(camera__name=cam)

class HourlyStatsList(generics.ListAPIView):

    serializer_class = HourlyStatsSerializer

    queryset = HourlyStats.objects.all()

    def get_queryset(self):

        cam = self.kwargs['camera']
        utcstart = self.kwargs['utcstart']
        timestamp_start = datetime.datetime.utcfromtimestamp(int(utcstart)/1000)
        #pytz.UTC.localize(timestamp_start)
        #timestamp_start = timestamp_start - datetime.timedelta(days=1)
        timestamp_end = timestamp_start + datetime.timedelta(days=1)
        return self.queryset.filter(camera__name=cam,hour__gte=timestamp_start,hour__lte=timestamp_end)
