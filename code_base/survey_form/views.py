from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from itertools import chain

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.utils.timezone import datetime

from django import forms
from django.forms import ModelForm

import re
import requests
import json
import jwt

from utils.configuration import kobo_constants, metabase_constants
from utils.constants import kobo_form_constants

from common.models import code
from location.models import location, location_program
from domain.models import domain, domain_program
from .models import survey, survey_question, survey_question_options
from survey_response.models import survey_response, survey_response_detail
from survey_response import views as response_views


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

    base_response = requests.get(kobo_constants.kobo_form_link,
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
    base_response = requests.get(kobo_constants.kobo_form_link,
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
def survey_delete(request, pk, template_name='survey_delete.html'):
    surveys=get_object_or_404(survey, pk=pk)
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
    form.pk = pk
    return render(request, template_name, {'form':form, 'survey':surveyForUpdate})


@login_required
def get_kobo_form(request,pk):
    survey_id = get_object_or_404(survey, pk=pk)
    print(survey_id)
    return render(request, {'survey': survey_id})


@login_required
def survey_view(request, pk, template_name='survey_detail.html'):
    objsurvey= get_object_or_404(survey, pk=pk)
    print(objsurvey.kobo_form_id)
    if request.method == 'POST':
        #print(request.POST)

        if 'pull-form-data' in request.POST:
            #print("kobo form data")
            response_views.pull_kobo_form_data(objsurvey)

        elif 'pull-response-data' in request.POST:
            #print("form response data")
            response_views.pull_kobo_response_data(objsurvey)

    show_delete_survey_button = True
    survey_response_exists = survey_response.objects.filter(survey_id=objsurvey).first()
    if survey_response_exists:
        survey_response_detail_exists = survey_response_detail.objects.filter(survey_response_id=survey_response_exists).first()

        if survey_response_detail_exists:
            show_delete_survey_button = False
    print(objsurvey.survey_id)
    payload = {
        "resource": {"dashboard": 2},
        "params": {
            "survey_id": objsurvey.survey_id
        }
    }
    token = jwt.encode(payload, metabase_constants.metabase_secret_key, algorithm="HS256")
    iframeUrl = metabase_constants.metabase_site_url + "/embed/dashboard/" + token.decode('utf8') + "#bordered=false&titled=false"

    return render(request, template_name, {'object': objsurvey, 'show_delete': show_delete_survey_button,
                                           'iframeUrl': iframeUrl})



def survey_domain_suggestion(request, survey_id):
    #domain_list = domain.objects.all()
    obj_survey = survey.objects.get(survey_id = survey_id)
    surveyID = survey_question.objects.filter(survey_id=survey_id).values('domain_id').distinct()
    print(surveyID)
    domain_list = domain.objects.filter(domain_id__in=surveyID)
    obj_location = location.objects.get(location_id = obj_survey.location_id.location_id)
    data_json = serializers.serialize('json', domain_list)
    data_list = json.loads(data_json)
    for item in data_list:
        index_value = response_views.get_domain_index(item, survey_id)
        item.update({"index": index_value})
        item.update({"location_id": obj_location.location_id}) # location id of conducted survey


    data = json.dumps(data_list)

    return HttpResponse(data, content_type='application/json')


# location program list form
class LocationProgram_Form(ModelForm):
    YEARS = [x for x in range(1990, 2021)]


    date_of_implementation = forms.DateField(required=True,
                                           label='Date of implementation', initial= datetime.now(),
                                           widget=forms.SelectDateWidget(empty_label="", years=YEARS))

    class Meta:
        model = location_program
        fields = ['date_of_implementation', 'notes']


@login_required
def survey_program_list(request, pk, location_id, template_name='survey_program_list.html'):
    obj_domain = domain.objects.get(domain_id=pk)
    obj_location = location.objects.get(location_id= location_id)
    return render(request, template_name, {'obj_domain': obj_domain , 'obj_location':obj_location})


@login_required
def get_location_program_list_for_datatable(request, pk, location_id):
    program_list = domain_program.objects.filter(domain_id=pk).values('domain_program_id','program_name','description')
    for item in program_list:
        program_id = item['domain_program_id']
        if location_program.objects.filter(program_id=program_id, location_id=location_id ).exists():
            obj_location_program = location_program.objects.filter(program_id=program_id, location_id=location_id ).\
                values('location_program_id', 'date_of_implementation','notes','location_id_id')
            for i in obj_location_program:
                item.update(i)
        else:
            i = {'date_of_implementation': None, 'notes': None , 'location_id_id': location_id}
            item.update(i)
    data1 = list(program_list)
    data = json.dumps(data1, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')

#function for update implemented programs
@login_required
def location_program_update(request, pk, location_id, template_name='survey_location_program_update.html'):
   location_name = location.objects.get(pk = location_id)
   obj_program = domain_program.objects.get(pk=pk)
   if location_program.objects.filter(program_id=pk, location_id=location_id).exists():
       obj_loc_program = location_program.objects.get(program_id=obj_program, location_id=location_id)
       programForUpdate = get_object_or_404(location_program, pk=obj_loc_program.location_program_id)
       form = LocationProgram_Form(instance=programForUpdate)
       if request.method == 'POST':
           form = LocationProgram_Form(request.POST, instance=programForUpdate)
           if form.is_valid():
               info = form.save()
               info.modified_by = request.user
               info.save()
               return redirect('/survey/survey_program_list/' + str(obj_program.domain_id.domain_id) + '/' + str(location_id))
           else:
               print(form.errors)
       form.pk = pk
   else:
       if request.method == 'POST':
           form = LocationProgram_Form(request.POST)
           print(request.POST)
           if form.is_valid():
               info = form.save(commit=False)
               info.program_id = obj_program
               info.location_id = location_name
               info.created_by = request.user
               info.modified_by = request.user
               info.save()
               return redirect('/survey/survey_program_list/' + str(obj_program.domain_id.domain_id) + '/' + str(location_id))
           else:
               print(form.errors)
       else:
           form = LocationProgram_Form
   return render(request, template_name, {'form': form , 'obj_program': obj_program, 'location_name': location_name})