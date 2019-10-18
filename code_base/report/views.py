
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django.shortcuts import render
from utils.configuration import kobo_constants, metabase_constants
from utils.constants import kobo_form_constants
from .test_pdf import render_to_pdf
from django.views.generic import TemplateView
from common.models import code
from location.models import location, location_program
from domain.models import domain, domain_program
from survey_form.models import survey, survey_question, survey_question_options
from survey_response.models import survey_response, survey_response_detail
from survey_response import views as response_views

# Create your views here.

def get_survey_question_list_for_pdf(request, pk):
    survey_questions_list = survey_question.objects.filter(survey_id = pk )
    data = serializers.serialize('json', survey_questions_list)
    return HttpResponse(data, content_type='application/json')


def InvoicePDFView(request,pk):
    #Retrieve data or whatever you need
    # obj_domain = domain.objects.get(pk=domain_id)
    obj_survey = survey.objects.get(survey_id = pk)
    return render_to_pdf(
            'generate_pdf.html',
            {
                'pagesize':'A4',
                'object': obj_survey,
            }
        )