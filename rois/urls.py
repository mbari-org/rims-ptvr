from django.conf.urls import url, include
from rest_framework import routers
from rois import views

router = routers.DefaultRouter()
#router.register(r'images',views.ImageViewSet)

urlpatterns = [
        #url(r'^$', views.ImageList.as_view(), name='image-list'),
        #url(r'^(?P<pk>[0-9]+)/$',views.ImageDetail.as_view(),name='image-detail'),
        url(r'^',include(router.urls)),
        url(r'browser$',views.browser,name='browser'),
        url(r'totals/(?P<camera>.+)/$',views.totals,name='totals'),
        url(r'find_image/(?P<image_id>.+)/$',views.find_image,name='find_image'),
        url(r'labels/$',views.labels,name='labels'),
        url(r'tags/$',views.tags,name='tags'),
        url(r'label_images$',views.label_images,name='label_images'),
        # url(r'get_histograms/(?P<camera>.+)/(?P<utcstart>.+)/(?P<utcend>.+)/$',views.get_histograms,name='get_histograms'),
#        url(r'get_histograms/$',views.get_historgrams,name='get_histograms'),
        url(r'get_user$',views.get_user,name='get_user'),
        url(r'login_user$',views.login_user,name='login_user'),
        url(r'logout_user$',views.logout_user,name='logout_user'),
        
        url(r'images/(?P<camera>.+)/(?P<utcstart>.+)/(?P<utcend>.+)/(?P<hourstart>.+)/(?P<hourend>.+)/(?P<nimages>.+)/(?P<minlen>.+)/(?P<maxlen>.+)/(?P<minaspect>.+)/(?P<maxaspect>.+)/(?P<exclude>.+)/(?P<ordering>.+)/(?P<archive>.+)/(?P<label>.+)/(?P<labeltype>.+)/(?P<tag>.+)/$',views.ImageList.as_view()),
#        url(r'imagearchive/(?P<camera>.+)/(?P<utcstart>.+)/(?P<utcend>.+)/(?P<hourstart>.+)/(?P<hourend>.+)/(?P<minlen>.+)/(?P<maxlen>.+)/(?P<minaspect>.+)/(?P<maxaspect>.+)/(?P<exclude>.+)/(?P<label>.+)/(?P<tag>.+)/$',views.ImageArchive.as_view()),
        url(r'^api-auth/',include('rest_framework.urls',namespace='rois_rest_framework'))

        ]
