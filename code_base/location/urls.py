from django.urls import path

from . import views

urlpatterns = [

    # path('add_location/', views.add_location, name='add_location'),
    # path('list_location/', views.list_location, name='list_location'),
    # path('update_location/', views.update_location, name='update_location'),
    path('', views.location_list, name='location_list'),
    path('view/<int:pk>', views.location_view, name='location_view'),
    path('new', views.location_create, name='location_new'),
    path('edit/<int:pk>', views.location_update, name='location_edit'),
    path('delete/<int:pk>', views.location_delete, name='location_delete'),
    path('survey_list/<int:pk>', views.get_location_survey_list_for_datatable, name='get_location_survey_list_for_datatable'),
    path('get_location_list_for_datatable', views.get_location_list_for_datatable, name='get_location_list_for_datatable')
]

