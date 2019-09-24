from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    #path('json1', views.survey_list1Json.as_view(), name='survey_list_json'),
    path('', views.survey_list1.as_view(), name='survey_list'),
    path('get_survey_list_for_datatable', views.get_survey_list_for_datatable, name='get_survey_list_for_datatable'),
    path('new', views.survey_create, name='survey_new'),
    path('view/<int:pk>', views.survey_view, name='survey_view'),
    path('delete/<int:pk>', views.survey_delete, name='survey_delete'),
    path('edit/<int:pk>', views.survey_update, name='survey_edit'),
]