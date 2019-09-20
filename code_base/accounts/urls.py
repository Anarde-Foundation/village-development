from django.conf.urls import url
from django.urls import path, include
from accounts import views
from django.contrib.auth.decorators import login_required



urlpatterns = [

    path('register/',views.register_view, name='register'),
    path('user_new/',views.add_user, name='user_add'),
    path('user_update/<int:pk>',views.update_view, name='user_update'),
    path('user_list', views.user_list.as_view(), name='user_list'),
    path('user_json',views.user_listJson.as_view(), name='user_list_json'),



]
