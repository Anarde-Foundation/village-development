from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.funder_list.as_view(), name='funder_list'),
    path('funder_create/',views.funder_create, name='funder_create'),
    path('view/<int:pk>', views.funder_view, name='funder_view'),
    path('edit/<int:pk>', views.funder_update, name='funder_edit'),
    path('delete/<int:pk>', views.funder_delete, name='funder_delete'),
    path('funder_list', views.funder_list.as_view(), name='funder_list'),
    path('get_funder_list_for_datatable',views.get_funder_list_for_datatable, name='get_funder_list_for_datatable'),

    path('program_list/<int:pk>', views.get_funder_program_list_for_datatable, name='get_funder_program_list_for_datatable'),
    path('add_program/<int:id>', views.add_program, name='add_program'),
    path('view_program/<int:pk>', views.view_program, name='view_program'),
    path('update_program/<int:pk>', views.update_program, name='update_program'),

    path('load_location_programs/<int:pk>', views.load_location_programs, name='load_location_programs'),
]