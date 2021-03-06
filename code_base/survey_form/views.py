from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.core import serializers
from itertools import chain

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView

import json
import jwt

from utils.configuration import kobo_constants, metabase_constants, image_constants, aws_bucket_constants
from utils.constants import kobo_form_constants, numeric_constants, code_group_names

from common.models import code, code_group
from location.models import location, location_program, location_program_image
from domain.models import domain, domain_program
from .models import survey, survey_question
from .forms import get_kobo_form_date, SurveyForm, LocationProgram_Form
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


@login_required
def survey_create(request, template_name='survey_create.html'):
    if request.method == 'POST':
        form = SurveyForm(request.POST, surveyID=None)
        print(form.data)
        if form.is_valid():
            publish_date = get_kobo_form_date(int(form.cleaned_data['kobo_form_id']))
            info = form.save(commit=False)
            info.publish_date = publish_date
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/survey/')
        else:
            print(form.errors)
    else:

        form = SurveyForm(initial={'kobo_form_id': 'Select an Option'},surveyID=None)

    return render(request, template_name, {'form':form})


@login_required
def survey_delete(request, pk, template_name='survey_delete.html'):
    surveys = get_object_or_404(survey, pk=pk)
    if request.method == 'POST':
        surveys.delete()
        return redirect('/survey/')

    return render(request, template_name, {'object': surveys})


@login_required
def survey_update(request, pk, template_name='survey_update.html'):
    surveyForUpdate = get_object_or_404(survey, pk=pk)
    form = SurveyForm(instance=surveyForUpdate, surveyID=pk)
    if request.method == 'POST':
        print(request.POST)
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/survey/view/'+ str(pk))

        form = SurveyForm(request.POST, instance=surveyForUpdate, surveyID=pk)
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
    objsurvey = get_object_or_404(survey, pk=pk)
    error_log = []
    # Pull kobo form data
    if request.method == 'POST':
        # print(request.POST)

        if 'pull-form-data' in request.POST:
            # print("kobo form data")
            error_log = response_views.pull_kobo_form_data(objsurvey)

        elif 'pull-response-data' in request.POST:
            response_views.pull_kobo_response_data(objsurvey)

    print(error_log)
    # Show / Hide delete button
    show_delete_survey_button = True
    survey_response_exists = survey_response.objects.filter(survey_id=objsurvey).first()
    if survey_response_exists:
        survey_response_detail_exists = survey_response_detail.objects.filter(survey_response_id=survey_response_exists).first()

        if survey_response_detail_exists:
            show_delete_survey_button = False

    return render(request, template_name, {'object': objsurvey, 'show_delete': show_delete_survey_button,
                                           'error_log':error_log , 'iframeUrl': '', 'domain_id':1})


def get_iframeURL(objDomain, survey_id):
    # Payload for metabase graphs
    payload = {
        "resource": {"dashboard": objDomain.metabase_dashboard_id},
        "params": {
            "survey_id": survey_id
        }
    }

    # Build iframe url
    token = jwt.encode(payload, metabase_constants.metabase_secret_key, algorithm="HS256")
    iframeUrl = metabase_constants.metabase_site_url + "/embed/dashboard/" + token.decode(
        "utf8") + "#bordered=false&titled=false"

    return iframeUrl


def show_domainwise_metabase_graph(request, survey_id, domain_id):
    # Get domain object
    # objDomain = get_object_or_404(domain, pk=domain_id)
    try:
        objDomain = domain.objects.get(pk = domain_id)
    except domain.DoesNotExist:
        objDomain = None

    if objDomain == None or objDomain.metabase_dashboard_id == None:
        responseData = {}
        responseData['iframeUrl'] = ''
    else:
        iframeUrl = get_iframeURL(objDomain, survey_id)
        responseData = {}
        responseData['iframeUrl'] = iframeUrl

    data = json.dumps(responseData) #{'iframeUrl': iframeUrl}
    return HttpResponse(data, content_type='application/json')


def survey_domain_suggestion(request, survey_id):
    """
    Returns a list of domains based on survey
    :param request:
    :param survey_id: The survey id, whose domains are to be found out
    :return:
    """
    # Get list of distinct domain ids, applicable for the current survey
    distinct_domain_ids = survey_question.objects.values('domain_id').filter(survey_id = survey_id).distinct()

    # Get list of domain objects based on distinct domain list above
    domain_list = domain.objects.filter(domain_id__in=[item['domain_id'] for item in distinct_domain_ids])

    obj_survey = survey.objects.get(survey_id = survey_id)
    obj_location = location.objects.get(location_id = obj_survey.location_id.location_id)
    data_json = serializers.serialize('json', domain_list)
    data_list = json.loads(data_json)
    for item in data_list:
        index_value = response_views.get_domain_index(item['fields']['kobo_group_key'], survey_id)
        item.update({"index": index_value})
        item.update({"location_id": obj_location.location_id}) # location id of conducted survey

    data = json.dumps(data_list)

    return HttpResponse(data, content_type='application/json')


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


@login_required
@csrf_exempt
def location_program_update_image_upload(request, location_id, domain_program_id):
    obj_program = domain_program.objects.get(pk=domain_program_id)
    print(obj_program)

    if location_program.objects.filter(location_id=location_id, program_id=obj_program).exists():
        objlocation = location_program.objects.get(location_id=location_id, program_id=obj_program)

        print(objlocation)
        print("in upload image")
        if request.is_ajax():
            print(request.FILES)
            location_names = []
            image_names = []
            image_list = []
            for filename, file in request.FILES.items():
                single_image = request.FILES[filename]
                print(single_image)

                if 'before' in filename.lower():
                    location1, image_name = response_views.save_images(single_image, image_constants.image_type_before)

                    image_type = code.objects.filter(code_id=numeric_constants.before_images).first()
                    print(image_type)
                else:
                    location1, image_name = response_views.save_images(single_image, image_constants.image_type_after)
                    image_type = code.objects.filter(code_id=numeric_constants.after_images).first()

                location_program_image(image_name=image_name, created_by=request.user, location_program_id=objlocation,
                                       image_type_code_id=image_type).save()

                image_id = location_program_image.objects.last().location_program_image_id
                image_list.append(image_id)
                if image_constants.is_production:
                    location_names.append(location1)
                else:
                    localhost_location = location1
                    location_names.append(localhost_location)
                print(location_names)
                image_names.append(image_name)
            print(location_names)
            data = {'is_valid': True, 'name': image_names, 'url': location_names, 'images': image_list}
        else:
            data = {'is_valid': False}
    else:
        data = {'is_valid': False, 'message': "program not yet implemented. please set implementation date"}
    data = json.dumps(data)
    print(data)
    return HttpResponse(data, content_type='application/json')


# function to delete images
@login_required
@csrf_exempt
def survey_location_program_update_image_delete(request, image_name):
    print(image_name)
    images = location_program_image.objects.filter(image_name=image_name).first()
    print(images)
    # images = get_object_or_404(location_program_image, image_name=image_name)
    if images:
        images.delete()
        print('deleted')

        data = {'is_valid': True, 'image_id': image_name}
    else:
        data = {'is_valid': False}

    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


# function for updating implemented programs
@login_required
def location_program_update(request, pk, location_id, template_name='survey_location_program_update.html'):
    location_name = location.objects.get(pk=location_id)
    obj_program = domain_program.objects.get(pk=pk)

    before_images = []
    after_images = []

    if location_program.objects.filter(program_id=pk, location_id=location_id).exists():
        program_implemented = "true"
        obj_loc_program = location_program.objects.get(program_id=obj_program, location_id=location_id)
        location_images = location_program_image.objects.filter(location_program_id=obj_loc_program)

        before_images_id = code.objects.filter(code_id=numeric_constants.before_images).first()
        before_images = location_images.filter(image_type_code_id=before_images_id).values_list('image_name', flat=True)

        after_images = location_images.exclude(image_type_code_id=before_images_id).values_list('image_name', flat=True)

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
        program_implemented = "false"
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
    print(before_images)
    print("--------")
    print(after_images)
    if image_constants.is_production:
        path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                      image_constants.image_dir
    else:
        path = image_constants.before_afterDirStatic
    return render(request, template_name, {'form': form, 'obj_program': obj_program, 'location_name': location_name,
                                           'path': path, 'program_implemented': program_implemented,
                                           'before_photos': before_images, 'after_photos': after_images})


@login_required
def survey_question_list(request,pk, domain_id, template_name='survey_question_list.html'):
    obj_domain = domain.objects.get(pk=domain_id)
    obj_survey = survey.objects.get(pk=pk)
    return render(request, template_name, {'obj_domain': obj_domain, 'obj_survey': obj_survey})


@login_required
def get_survey_question_list_for_datatable(request, pk, domain_id):
    survey_questions_list = survey_question.objects.filter(survey_id = pk , domain_id= domain_id)
    data = serializers.serialize('json', survey_questions_list)
    return HttpResponse(data, content_type='application/json')

# ===================> for pdf <==============================


