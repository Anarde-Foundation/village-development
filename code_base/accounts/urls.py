from django.conf.urls import url
from django.urls import path, include
from accounts import views
from django.contrib.auth.decorators import login_required



urlpatterns = [

    path('register/',views.register_view, name='register'),
    path('account_create/',views.account_create, name='account_create'),
    path('account_update/<int:pk>',views.account_update, name='account_update'),
    path('account_list', views.account_list.as_view(), name='account_list'),
    path('get_user_list_for_datatable',views.get_user_list_for_datatable, name='get_user_list_for_datatable'),



]
