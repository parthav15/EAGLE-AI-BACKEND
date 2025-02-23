from django.urls import path
from surveillance import views

urlpatterns = [
    # STREAMING URL
    path('video/', views.video_stream, name='video_stream'),

    # CAMERA URL'S
    path('get_cameras/', views.list_cameras, name='list_cameras'),
    path('get_specific_camera/<int:camera_id>/', views.get_camera, name='get_camera'),
    path('add_camera/', views.add_camera, name='add_camera'),
    path('update_camera/<int:camera_id>/', views.update_camera, name='update_camera'),
    path('delete_camera/<int:camera_id>/', views.delete_camera, name='delete_camera')
]