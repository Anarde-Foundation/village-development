from django.conf.urls import url
from django.urls import path, include
from accounts import views


urlpatterns = [

    path('register/',views.register_view, name='register'),

]
