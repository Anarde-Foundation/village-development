from django.conf.urls import url
from django.urls import path, include
from accounts import views
from django.contrib.auth.decorators import login_required



urlpatterns = [

    path('register/',views.register_view, name='register'),


]
