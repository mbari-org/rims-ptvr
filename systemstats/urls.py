from django.conf.urls import url, include
from rest_framework import routers
from systemstats import views

router = routers.DefaultRouter()
#router.register(r'images',views.ImageViewSet)

urlpatterns = [
        #url(r'^$', views.ImageList.as_view(), name='image-list'),
        #url(r'^(?P<pk>[0-9]+)/$',views.ImageDetail.as_view(),name='image-detail'),
        url(r'^',include(router.urls)),
        url(r'minutestats/(?P<camera>.+)/$',views.MinuteStatsList.as_view()),

        ]
