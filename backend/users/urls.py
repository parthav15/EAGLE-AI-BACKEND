from django.urls import path
from users import views

urlpatterns = [
    # USER URL'S
    path('user_register/', views.user_register, name='user_register'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_details/', views.get_user_details_view, name='user_details'),
    path('edit_user_details/', views.edit_user_details_view, name='edit_user_details'),
    path('edit_profile_picture/', views.edit_profile_picture_view, name='edit_profile_picture'),
]
