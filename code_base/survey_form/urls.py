from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    # path('connect-kobo/', views.connect_kobo, name='connect'),
    path('', views.survey_list1.as_view(), name='survey_list'),
    path('json1', views.survey_list1Json.as_view(), name='survey_list_json'),
    path('new', views.survey_create, name='survey_new'),

]