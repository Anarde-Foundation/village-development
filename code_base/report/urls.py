from django.conf.urls import url
from django.urls import path, include
from . import views


app_name = 'report'
urlpatterns = [
path('pdf/<int:pk>', views.InvoicePDFView, name='pdf'),
path('get_survey_question_list_for_pdf/<int:pk>', views.get_survey_question_list_for_pdf, name='get_survey_question_list_for_pdf'),
    ]