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
from utils.constants import kobo_form_constants

from common.models import code
from location.models import location, location_program
from domain.models import domain, domain_program
from .models import survey, survey_question, survey_question_options
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

        pull_kobo_form_data(objsurvey)
        response_views.pull_kobo_response_data(objsurvey)

    return render(request, template_name, {'object': objsurvey})


def pull_kobo_form_data(surveyID):

    print(surveyID)
    kobo_form_id = surveyID.kobo_form_id
    data_link = kobo_constants.kobo_form_link+ "/" + str(kobo_form_id) + kobo_form_constants.data_format
    print(data_link)
    survey_form_data = requests.get(data_link, headers={'Authorization': kobo_constants.authorization_token}).json()
    #print(json.dumps(survey_data, indent=4))
    survey_children = survey_form_data['children']
    print("survey_name: ", survey_form_data['title'])

    for i in range(len(survey_children)):
        if survey_children[i]['type'] == 'group':
            grp_name = survey_children[i]['name']
            print("****************")
            for j in range(len(survey_children[i]['children'])):
                get_kobo_questions_and_options(survey_children[i]['children'], j, surveyID, grp_name)

        else:
            print("----------------")
            get_kobo_questions_and_options(survey_children, i, surveyID)


def get_kobo_questions_and_options(survey_children, i, surveyID, grp_name=None):
    print(grp_name)
    question_label = ""
    option_label = ""
    grp_key = ""
    if grp_name:
        domainname = re.search('_(.+?)_', grp_name)
        if domainname:
            grp_key = domainname.group(1)

    domainID = domain.objects.filter(kobo_group_key=grp_key).first()

    if survey_children[i]['type'] != 'group':
        if survey_children[i]['name'] not in kobo_form_constants.names_not_allowed:
            print("question name: ", survey_children[i]['name'])
            question_name = survey_children[i]['name']

            survey_questionID = survey_question.objects.filter(survey_id=surveyID, question_name=question_name).first()
            if not survey_questionID:
                if 'label' in survey_children[i].keys():
                    print("question label ", survey_children[i]['label'])
                    question_label = survey_children[i]['label']

                question_type = survey_children[i]['type']
                survey_question(survey_id=surveyID, section_id=grp_name, domain_id=domainID,
                                question_label=question_label, question_name=question_name,
                                question_type=question_type).save()

                if survey_children[i]['type'] in kobo_form_constants.question_type_having_options:
                    question_children = survey_children[i]['children']
                    questionID= survey_question.objects.filter(question_name=question_name).first()

                    for k in range(len(question_children)):
                        print("options : ", question_children[k]['name'])
                        option_name = question_children[k]['name']
                        if 'label' in question_children[k].keys():
                            print("option label ", question_children[k]['label'])
                            option_label = question_children[k]['label']

                        survey_question_options(survey_question_id=questionID,option_name=option_name,
                                                option_label=option_label).save()
            else:
                print('question exists')

def pull_kobo_form_data(surveyID):

    print(surveyID)
    kobo_form_id = surveyID.kobo_form_id
    data_link = kobo_constants.kobo_form_link+ "/" + str(kobo_form_id) + kobo_form_constants.data_format
    print(data_link)
    survey_data = requests.get(data_link, headers={'Authorization': kobo_constants.authorization_token}).json()
    #print(json.dumps(survey_data, indent=4))
    survey_children = survey_data['children']
    print("survey_name: ", survey_data['title'])
    grp_name = ""

    for i in range(len(survey_children)):
        if survey_children[i]['type'] == 'group':
            grp_name = survey_children[i]['name']
            print("****************")
            for j in range(len(survey_children[i]['children'])):
                get_kobo_questions_and_options(survey_children[i]['children'], j, surveyID,grp_name)

        else:
            print("----------------")
            get_kobo_questions_and_options(survey_children, i,surveyID)

def survey_domain_suggestion(request, survey_id):
    domain_list = domain.objects.all()
    obj_survey = survey.objects.get(survey_id = survey_id)
    obj_location = location.objects.get(location_id = obj_survey.location_id.location_id)
    data_json = serializers.serialize('json', domain_list)
    data_list = json.loads(data_json)
    for item in data_list:
        item.update({"index": "100"}) #static index
        item.update({"location_id": obj_location.location_id}) # location id of conducted survey

    data = json.dumps(data_list)

    return HttpResponse(data, content_type='application/json')

# location program list form
class LocationProgram_Form(ModelForm):
    YEARS = [x for x in range(1990, 2021)]

    location_queryset = location.objects.all()
    location_id = forms.ModelChoiceField(queryset=location_queryset, empty_label='Select an Option',
                                         label='Location', required=True)
    date_of_implementation = forms.DateField(required=True,
                                           label='Date of implementation', initial= datetime.now(),
                                           widget=forms.SelectDateWidget(empty_label="", years=YEARS))

    class Meta:
        model = location_program
        fields = [ 'location_id', 'date_of_implementation', 'notes']

@login_required
def survey_program_list(request, pk, template_name='survey_program_list.html'):
    obj_domain =  get_object_or_404(domain, pk=pk)
    obj_domain = domain.objects.get(domain_id=pk)
    return render(request, template_name, {'obj_domain': obj_domain})

@login_required
def get_location_program_list_for_datatable(request, pk):
    domain_list = domain.objects.filter(pk=pk).select_related()
    obj_location = location_program.objects.filter(program_id__in =domain_program.objects.filter(domain_id=pk) )
    print(obj_location)
    program_list = domain_program.objects.filter(domain_id=pk).prefetch_related()
    location_program_list = []
    for program in program_list:
        if location_program.objects.filter(program_id =program.domain_program_id).exists():
            location_programs = location_program.objects.filter(program_id =program.domain_program_id)
            location_program_list.append(location_programs)
    print("+++++++++++++location_program_list++++++++++++")
    print(location_program_list)
    print("++++++++++++program_list+++++++++++++")
    print(program_list)
    suggested_program_list = list(domain_program.objects.filter(domain_id=pk).values_list(
        "program_name", "description"
    ).union(
        location_program.objects.all().values_list(
            "date_of_implementation", "location_id"
        )))
    # vendor = Vendor.objects.get(pk=vendor_id).prefetch_related(vendor_purchases).prefetch_related(
    #     vendor_purchases__user)
    #
    # user_list = []
    #
    # for purchase in vendor.vendor_purchases.all():
    #     purchase_user = {}
    #     purchase_user["id"] = purchase.user.pk
    #     purchase_user["email"] = purchase.user.email
    #     purchase_user["first_name"] = purchase.user.first_name
    #     purchase_user["last_name"] = purchase.user.last_name
    #     user_list.append(purchase_user)
    #
    # result = {}
    # result["id"] = vendor.pk
    # result["name"] = vendor.name
    # result["users"] = user_list
    print(suggested_program_list)
    data = serializers.serialize('json', obj_location)
    # data = json.dumps(program_list)
    return HttpResponse(data, content_type='application/json')

#function for update implemented programs
@login_required
def location_program_update(request, pk, template_name='survey_location_program_update.html'):
    obj_program = domain_program.objects.get(pk=pk)
    if request.method == 'POST':
        form = LocationProgram_Form(request.POST)
        print(request.POST)
        if form.is_valid():
            print('form valid.............')
            info = form.save(commit=False)
            info.program_id = obj_program
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/survey/survey_program_list/' + str(obj_program.domain_id.domain_id))
        else:
            print(form.errors)
    else:
        form = LocationProgram_Form
    return render(request, template_name, {'form': form , 'obj_program': obj_program})