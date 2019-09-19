from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.utils.timezone import datetime
from django import forms
from django.forms import ModelForm

import requests
import json
# from utils.configurator import kobo_constants
from common.models import code
from location.models import location
from .models import survey, survey_question, survey_question_options

@login_required
def connect_kobo(request):

    # base_response = requests.get(kobo_constants.form_info_link, headers={'Authorization':kobo_constants.authorization_token})
    # print(base_response)
    print("hello")
    return HttpResponse("hello")


class survey_list1(TemplateView):
    template_name = 'survey_list.html'


class survey_list1Json(BaseDatatableView):
    model = survey
    columns = ['survey_id','survey_name', 'survey_type_code_id.code_name', 'publish_date', 'created_by', 'location_id.location_name']
    order_columns = ['survey_name', 'survey_type_code_id.code_name', 'publish_date', 'created_by', 'location_id']


class SurveyForm(ModelForm):

    location_id = forms.ModelChoiceField(queryset=location.objects.all().order_by('location_name'))
    survey_name = forms.CharField(required= True, label='Survey name', max_length=100)


    class Meta:
        model = survey
        fields = ['location_id','kobo_form_id','survey_name']


def survey_create(request, template_name='survey_create.html'):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            info =form.save()
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/survey/')
        else:
            print(form.errors)
    else:

        form = SurveyForm
    return render(request, template_name, {'form':form})



def survey_list(request, template_name='survey_list.html'):
    survey_list = survey.objects.all().values()  #filter().order_by('survey_id')
    print(survey_list)
    #survey_list1 = serializers.serialize('json', survey_list)
    #survey_json = json.dumps({"data": list(survey_list)})
    #print(type(survey_list1))

    #test_all = json.dumps({"data": list(survey_list)})
    #data = {'test_data': test_all, }
    return render(request, template_name, {'survey_list': survey_list})
