from django.urls import path

from . import views

urlpatterns = [
    path('', views.domain_list, name='domain_list'),
    path('domain_create', views.domain_create, name='domain_create'),
    path('view/<int:pk>', views.domain_view, name='domain_view'),
    path('edit/<int:pk>', views.domain_update, name='domain_update'),
    # path('delete/<int:pk>', views.domain_delete, name='domain_delete'),
    path('program_list/<int:pk>', views.get_domain_program_list_for_datatable, name='get_domain_program_list_for_datatable'),
    path('program_create/<int:id>', views.program_create, name='program_create'),
    path('program_view/<int:pk>', views.program_view, name='program_view'),
    path('program_edit/<int:pk>', views.program_update, name='program_update'),
    # path('delete/<int:pk>', views.program_delete, name='domain_delete'),

    path('json', views.get_domain_list_for_datatable,
         name='get_domain_list_for_datatable'),


]