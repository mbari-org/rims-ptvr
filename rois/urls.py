from django.urls import path, re_path, include
from rest_framework import routers
from rois import views

# image list query parameters
image_list_params = '/'.join([
        '<str:camera>',             
        '<str:utcstart>',
        '<str:utcend>',
        '<str:hourstart>',
        '<str:hourend>',
        '<str:mindepth>',
        '<str:maxdepth>',
        '<str:nimages>',
        '<str:minlen>',
        '<str:maxlen>',
        '<str:minaspect>',
        '<str:maxaspect>',
        '<str:exclude>',
        '<str:ordering>',
        '<str:archive>',
        '<str:label>',
        '<str:labeltype>',
        '<str:tag>',
        '<str:annotator>'  
])

router = routers.DefaultRouter()

urlpatterns = [
        path('totals/<str:camera>/', views.totals, name='totals'),
        path('find_image/<str:image_id>/',views.find_image,name='find_image'),
        path('labels',views.labels,name='labels'),
        path('annotators',views.annotators,name='annotators'),
        path('tags',views.tags,name='tags'),
        path('label_images',views.label_images,name='label_images'),
        path('get_user',views.get_user,name='get_user'),
        path('login_user',views.login_user,name='login_user'),
        path('logout_user',views.logout_user,name='logout_user'),
        path('images/' + image_list_params + '/',views.ImageList.as_view()),
        path('api-auth/',include('rest_framework.urls',namespace='rois_rest_framework'))

]
