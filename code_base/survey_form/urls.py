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
    path('survey_suggestion/<int:survey_id>', views.survey_domain_suggestion, name='survey_suggestion'),
    path('survey_program_list/<int:pk>/<int:location_id>', views.survey_program_list, name='survey_program_list'),
    path('show_domainwise_metabase_graph/<int:survey_id>/<int:domain_id>',
         views.show_domainwise_metabase_graph, name='show_domainwise_metabase_graph'),
    path('survey_question_list/<int:pk>/<int:domain_id>', views.survey_question_list, name='survey_question_list'),
    path('survey_location_program_update/<int:pk>/<int:location_id>',
         views.location_program_update, name='survey_location_program_update'),
    path('survey_location_program_update_image_upload/<int:location_id>',
         views.location_program_update_image_upload, name='survey_location_program_update_image_upload'),
    path('survey_location_program_update_image_delete/<str:image_name>',
         views.survey_location_program_update_image_delete, name='survey_location_program_update_image_delete'),
    path('get_location_program_list_for_datatable/<int:pk>/<int:location_id>',
         views.get_location_program_list_for_datatable, name='get_location_program_list_for_datatable'),
    path('get_survey_question_list_for_datatable/<int:pk>/<int:domain_id>',
         views.get_survey_question_list_for_datatable, name='get_survey_question_list_for_datatable'),
]