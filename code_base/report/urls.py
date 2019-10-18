from django.conf.urls import url
from django.urls import path, include
from . import views


app_name = 'report'
urlpatterns = [
path('pdf/<int:pk>', views.InvoicePDFView, name='pdf'),
    ]