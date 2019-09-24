from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.utils.timezone import datetime

from django import forms
from django.forms import ModelForm

import re
import requests
import json

from utils.configuration import kobo_constants

from common.models import code
from location.models import location
from .models import survey, survey_question, survey_question_options


class survey_list1(TemplateView):
    template_name = 'survey_list.html'


class survey_list1Json(BaseDatatableView):
    model = survey
    columns = ['survey_id','survey_name', 'survey_type_code_id.code_name', 'publish_date', 'created_by', 'location_id.location_name']
    order_columns = ['survey_name', 'survey_type_code_id.code_name', 'publish_date', 'created_by', 'location_id.location_name']


@login_required
def get_survey_list_for_datatable(request):
    survey_list = survey.objects.all()
    data = serializers.serialize('json', survey_list, use_natural_foreign_keys=True)
    return HttpResponse(data, content_type='application/json')


def get_kobo_forms():

    base_response = requests.get(kobo_constants.form_info_link,
                                 headers={'Authorization': kobo_constants.authorization_token}).json()
    list_res =[]
    for i in range(len(base_response)):
        print(base_response[i]['formid'], " ", base_response[i]['title'], " ", base_response[i]['date_created'])
        match = re.search(r'\d{4}-\d{2}-\d{2}', base_response[i]['date_created'])
        date = datetime.strptime(match.group(), '%Y-%m-%d').date()
        res = (base_response[i]['formid'], base_response[i]['title'] + " (" + str(date) + ")")
        list_res.append(res)

    return tuple(list_res)


def get_kobo_form_date(kobo_id):
    base_response = requests.get(kobo_constants.form_info_link,
                                 headers={'Authorization': kobo_constants.authorization_token}).json()
    publish_date = datetime.now()
    for i in range(len(base_response)):
        if kobo_id == base_response[i]['formid']:
            match = re.search(r'\d{4}-\d{2}-\d{2}', base_response[i]['date_created'])
            publish_date = datetime.strptime(match.group(), '%Y-%m-%d').date()

    return publish_date


class SurveyForm(ModelForm):

    location_queryset = location.objects.all()
    location_id = forms.ModelChoiceField(queryset=location_queryset, empty_label='Select an Option',
                                         label='Location', required=True)

    kobo_forms = get_kobo_forms()
    kobo_form_id = forms.ChoiceField(required=True,label='Select Kobo Form', choices=kobo_forms)

    survey_name = forms.CharField(required= True, label='Survey name', max_length=100)

    code_queryset = code.objects.all()
    survey_type_code_id = forms.ModelChoiceField(queryset=code_queryset, empty_label='Select an Option',
                                                 label='Select Survey Type', required=True)

    class Meta:
        model = survey
        fields = ['location_id', 'kobo_form_id', 'survey_name', 'survey_type_code_id']


@login_required
def survey_create(request, template_name='survey_create.html'):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        print(form.data)
        if form.is_valid():
            publish_date = get_kobo_form_date(int(form.cleaned_data['kobo_form_id']))
            info = form.save(commit=False)
            info.publish_date=publish_date
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/survey/')
        else:
            print(form.errors)
    else:

        form = SurveyForm(initial={'kobo_form_name': 'Select an Option'})

    return render(request, template_name, {'form':form})


@login_required
def survey_view(request, pk, template_name='survey_detail.html'):
    objsurvey= get_object_or_404(survey, pk=pk)
    return render(request, template_name, {'object': objsurvey})


@login_required
def survey_delete(request, pk, template_name='survey_delete.html'):
    surveys= get_object_or_404(survey, pk=pk)
    if request.method=='POST':
        surveys.delete()
        return redirect('/survey/')

    return render(request, template_name, {'object': surveys})


@login_required
def survey_update(request, pk, template_name='survey_update.html'):
    surveyForUpdate = get_object_or_404(survey, pk=pk)
    form = SurveyForm(instance=surveyForUpdate)
    if request.method == 'POST':
        print(request.POST)
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/survey/view/'+ str(pk))

        form = SurveyForm(request.POST, instance=surveyForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/survey/view/'+ str(pk))
        else:
            print(form.errors)
    # else:
    #     form = LocationForm
    return render(request, template_name, {'form':form, 'survey':surveyForUpdate})
