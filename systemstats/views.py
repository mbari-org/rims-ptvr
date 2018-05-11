from django.http import HttpResponse
from django.template import RequestContext, loader
from systemstats.models import MinuteStats
from rest_framework import viewsets, generics, pagination
from systemstats.serializers import MinuteStatsSerializer
import datetime
import pytz

# Create your views here.

class MinutePagination(pagination.PageNumberPagination):
    page_size = 3000

class MinuteStatsList(generics.ListAPIView):

    serializer_class = MinuteStatsSerializer

    queryset = MinuteStats.objects.all()

    pagination_class = MinutePagination
    
    
    def get_queryset(self):

        cam = self.kwargs['camera']
        return self.queryset.filter(camera__name=cam)
