import inspect

from django.shortcuts import render, redirect, get_object_or_404

from django.core import serializers
from Anarde import settings as set
from django.shortcuts import render
from utils.constants import kobo_form_constants,  report_css_path, numeric_constants
from utils.configuration import kobo_constants, metabase_constants, image_constants, aws_bucket_constants

from location.models import location, location_program, location_program_image
from domain.models import domain, domain_program
from survey_form.models import survey, survey_question, survey_question_options
from survey_response import views as response_views
from survey_form.views import get_iframeURL
import json, requests

from django.http import HttpResponse
from weasyprint import HTML

from django.template.loader import render_to_string
from operator import itemgetter

from requests_html import HTMLSession
from requests_html import AsyncHTMLSession

import asyncio
from pyppeteer import launch
from django.forms.models import model_to_dict


async def render_iframe(iframe_name, domain_name, survey_id):
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    await page.goto(iframe_name, timeout=100000)
    path = image_constants.metabase_images
    name = domain_name + "_" + str(survey_id) + '.png'
    await asyncio.sleep(10)
    await page.screenshot({'path': path + name, 'fullPage': True})
    await browser.close()
    print("-----------------")
    return name


def report_images(survey_id, domains):

    if not domains.metabase_dashboard_id:
        return None

    # print(domains)
    # print(domains.metabase_dashboard_id)
    iframeurl = get_iframeURL(domains, survey_id)
    print(iframeurl)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    image_name = loop.run_until_complete(render_iframe(iframeurl, domains.kobo_group_key, survey_id))
    print(image_name)

    return image_name


def survey_html(request,pk,template_name='survey_report.html'):
    objsurvey = get_object_or_404(survey, pk=pk)
    # print(objsurvey.survey_id)
    # Get list of distinct domain ids, applicable for the current survey
    distinct_domain_ids = survey_question.objects.values('domain_id').filter(survey_id=pk).distinct()

    # Get list of domain objects based on distinct domain list above
    domain_list = domain.objects.filter(domain_id__in=[item['domain_id'] for item in distinct_domain_ids])

    # get location object
    obj_location = location.objects.get(location_id=objsurvey.location_id.location_id)

    domain_name_list = []
    domain_report_list = []
    for domains in domain_list:
        domain_report_values = {}
        data_json = model_to_dict(domains)
        # print(data_json)
        index_value = response_views.get_domain_index(data_json['domain_name'], pk)
        domain_name_list.append(data_json['domain_name'])
        # print(index_value)
        domain_report_values['index'] = index_value

        if float(index_value) < 25:
            colour_code = 'bg-danger'
            colour_text = 'text-danger'
        elif 25 <= float(index_value) < 50:
            colour_code = 'bg-danger-light'
            colour_text = 'text-danger-light'
        elif 50 <= float(index_value) < 75:
            colour_code = 'bg-color-2'
            colour_text = 'text-color-2'
        else:
            colour_code = 'bg-success'
            colour_text = 'text-success'

        domain_report_values['colour_bg'] = colour_code
        domain_report_values['colour_text'] = colour_text

        program_list = domain_program.objects.filter(domain_id=domains.domain_id).values('domain_program_id',
                                                                                         'program_name', 'description')

        for item in program_list:  # for each program
            program_id = item['domain_program_id']
            if location_program.objects.filter(program_id=program_id, location_id=obj_location.location_id).exists():
                obj_location_program = location_program.objects.filter(program_id=program_id,
                                                                       location_id=obj_location.location_id). \
                    values('location_program_id', 'date_of_implementation', 'notes', 'location_id_id')

                before_after_images = {}
                before_images = []
                after_images = []
                for i in obj_location_program:  # for each implemented program
                    # print(i)
                    # Get before After images
                    if location_program_image.objects.filter(location_program_id=i['location_program_id']).exists():
                        before_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.before_images).values_list('image_name', flat=True)

                        for image in before_image_name:
                            if image_constants.is_production:
                                before_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                                    image_constants.image_dir + image
                            else:
                                before_image_path = image_constants.localhost + image_constants.before_afterDirStatic + image
                            before_images.append(before_image_path)
                            before_after_images['before'] = before_images

                        after_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.after_images).values_list('image_name', flat=True)
                        for image in after_image_name:
                            if image_constants.is_production:
                                after_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                                   image_constants.image_dir + image
                            else:
                                after_image_path = image_constants.localhost + image_constants.before_afterDirStatic + image

                            after_images.append(after_image_path)
                            before_after_images['after'] = after_images
                        i.update(before_after_images)  # insert images in implemented program list
                    item.update(i)
            else:
                program_list.remove(item)

        # domain_program_list.append(program_list)         # assign program list to respective domain
        # print("*********", program_list)
        domain_report_values['program_list'] = program_list

        iframe_image = report_images(objsurvey.survey_id, domains)
        if iframe_image:
            if image_constants.is_production:
                iframe_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                    image_constants.image_dir + iframe_image
            else:
                iframe_image_path = image_constants.localhost + image_constants.metabase_images_localhost + iframe_image
            domain_report_values['iframe_image_path'] = iframe_image_path

        print("--------", domain_report_values)
        domain_report_list.append(domain_report_values)

    data = dict(zip(domain_name_list, domain_report_list))

    print(data)
    return render(request, template_name, {'object': objsurvey,
                                             'domain_index':data})


def html_to_pdf_generation_old(request,pk): #weasyprint pdf generatiosurvey_idn common function
    objsurvey = get_object_or_404(survey, pk=pk)
    print(objsurvey.survey_id)
    # Get list of distinct domain ids, applicable for the current survey
    distinct_domain_ids = survey_question.objects.values('domain_id').filter(survey_id=pk).distinct()

    # Get list of domain objects based on distinct domain list above
    domain_list = domain.objects.filter(domain_id__in=[item['domain_id'] for item in distinct_domain_ids])

    # get location object
    obj_location = location.objects.get(location_id=objsurvey.location_id.location_id)

    data_json = serializers.serialize('json', domain_list)
    data_list = json.loads(data_json)
    # Insert vulnerability index and location id in domain object
    for item in data_list:
        index_value = response_views.get_domain_index(item, pk)
        item.update({"index": index_value})
        item.update({"location_id": obj_location.location_id})  # location id of conducted survey
    field_list = list(map(itemgetter('fields'), data_list))
    index = list(map(itemgetter('index'), data_list))
    domain_name_list = list(map(itemgetter('domain_name'), field_list))
    color_bg = []
    color_text_list =[]
    # Assign color-codes according to index value for domain
    for i in index:
        color_code = 'bg-color-2'
        color_text = 'text-color-2'
        if float(i) < 25:
            color_code = 'bg-danger'
            color_text = 'text-danger'
        elif float(i) >= 25 and float(i) < 50:
            color_code = 'bg-danger-light'
            color_text = 'text-danger-light'
        elif float(i) >= 50 and float(i) < 75:
            color_code = 'bg-color-2'
            color_text = 'text-color-2'
        else:
            color_code = 'bg-success'
            color_text = 'text-success'
        color_bg.append(color_code)
        color_text_list.append(color_text)
    # print(color_bg)
    # get tuple of (index_value, ba_color, text_color) for domain
    color_index = tuple(zip(index, color_bg, color_text_list))
    print(color_index)
    # Get implemented program list for domain
    domain_program_list = []
    for domains in domain_list:
        program_list = domain_program.objects.filter(domain_id=domains.domain_id).values('domain_program_id','program_name','description')
        for item in program_list: # for each program
            program_id = item['domain_program_id']
            if location_program.objects.filter(program_id=program_id, location_id=obj_location.location_id).exists():
                obj_location_program = location_program.objects.filter(program_id=program_id,
                                                                       location_id=obj_location.location_id). \
                    values('location_program_id', 'date_of_implementation', 'notes', 'location_id_id')

                before_after_images = {}
                before_images = []
                after_images = []
                for i in obj_location_program: # for each implemented program
                    # print(i)
                    # Get before After images
                    if location_program_image.objects.filter(location_program_id=i['location_program_id']).exists():
                        before_image_name = location_program_image.objects.filter\
                            (location_program_id=i['location_program_id'],\
                             image_type_code_id = numeric_constants.before_images).values_list('image_name', flat=True)

                        for image in before_image_name:
                            if image_constants.is_production:
                                before_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image
                            else:
                                before_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image
                            before_images.append(before_image_path)
                            before_after_images['before'] = before_images

                        after_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.after_images).values_list('image_name', flat=True)
                        for image in after_image_name:
                            if image_constants.is_production:
                                after_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image
                            else:
                                after_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image

                            after_images.append(after_image_path)
                            before_after_images['after'] = after_images
                        i.update(before_after_images) # insert images in implemented program list
                    item.update(i)
            else:
                program_list.remove(item)

        domain_program_list.append(program_list)         # assign program list to respective domain

        iframe_image = report_images(objsurvey.survey_id, domains)
        if iframe_image:
            if image_constants.is_production:
                iframe_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                    image_constants.image_dir + iframe_image
            else:
                iframe_image_path = image_constants.localhost + image_constants.metabase_images_localhost + iframe_image
            # iframe_image_path.append(iframe_image_path)
            domain_program_list.append(iframe_image_path)

    #print(domain_program_list)
    value_list = list(zip(color_index,domain_program_list))

    data = dict(zip(domain_name_list, value_list))

    # iframe_images = report_images(objsurvey.survey_id)
    # iframe_image_paths = []
    # for image in iframe_images:
    #     if image_constants.is_production:
    #         iframe_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
    #                             image_constants.image_dir + image
    #     else:
    #         iframe_image_path = image_constants.localhost + image_constants.metabase_images_localhost + image
    #     iframe_image_paths.append(iframe_image_path)
    # print(iframe_image_paths)
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline;survey.pdf.pdf"

    html = render_to_string('survey_report.html', {'object': objsurvey,# 'iframe_images': iframe_image_paths,
                                                   'domain_index': data})
    print(response)
    print(set.BASE_DIR)
    HTML(string=html).write_pdf(response, stylesheets=report_css_path.stylesheet)#, font_config=font_config, stylesheets=[CSS('/home/aishwarya/Project/Anarde/Anarde/village-development/code_base/static/theme/vendors/bootstrap/dist/css/bootstrap.min.css')])
    return response


def html_to_pdf_generation(request, pk):         # weasyprint pdf generation
    objsurvey = get_object_or_404(survey, pk=pk)

    # Get list of distinct domain ids, applicable for the current survey
    distinct_domain_ids = survey_question.objects.values('domain_id').filter(survey_id=pk).distinct()

    # Get list of domain objects based on distinct domain list above
    domain_list = domain.objects.filter(domain_id__in=[item['domain_id'] for item in distinct_domain_ids])

    # get location object
    obj_location = location.objects.get(location_id=objsurvey.location_id.location_id)

    domain_name_list = []
    domain_report_list = []

    for domains in domain_list:

        domain_report_values = {}

        data_json = model_to_dict(domains)
        # print(data_json)
        index_value = response_views.get_domain_index(data_json['domain_name'], pk)
        domain_name_list.append(data_json['domain_name'])
        # print(index_value)
        domain_report_values['index'] = index_value

        if float(index_value) < 25:
            colour_code = 'bg-danger'
            colour_text = 'text-danger'
        elif 25 <= float(index_value) < 50:
            colour_code = 'bg-danger-light'
            colour_text = 'text-danger-light'
        elif 50 <= float(index_value) < 75:
            colour_code = 'bg-color-2'
            colour_text = 'text-color-2'
        else:
            colour_code = 'bg-success'
            colour_text = 'text-success'

        domain_report_values['colour_bg'] = colour_code
        domain_report_values['colour_text'] = colour_text

        program_list = domain_program.objects.filter(domain_id=domains.domain_id).values('domain_program_id','program_name','description')

        for item in program_list: # for each program
            program_id = item['domain_program_id']
            if location_program.objects.filter(program_id=program_id, location_id=obj_location.location_id).exists():
                obj_location_program = location_program.objects.filter(program_id=program_id,
                                                                       location_id=obj_location.location_id). \
                    values('location_program_id', 'date_of_implementation', 'notes', 'location_id_id')

                before_after_images = {}
                before_images = []
                after_images = []
                for i in obj_location_program: # for each implemented program
                    # print(i)
                    # Get before After images
                    if location_program_image.objects.filter(location_program_id=i['location_program_id']).exists():
                        before_image_name = location_program_image.objects.filter\
                            (location_program_id=i['location_program_id'],\
                             image_type_code_id = numeric_constants.before_images).values_list('image_name', flat=True)

                        for image in before_image_name:
                            if image_constants.is_production:
                                before_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image
                            else:
                                before_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image
                            before_images.append(before_image_path)
                            before_after_images['before'] = before_images

                        after_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.after_images).values_list('image_name', flat=True)
                        for image in after_image_name:
                            if image_constants.is_production:
                                after_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image
                            else:
                                after_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image

                            after_images.append(after_image_path)
                            before_after_images['after'] = after_images
                        i.update(before_after_images) # insert images in implemented program list
                    item.update(i)
            # else:
            #     program_list.remove(item)

        # print("*********", program_list)
        domain_report_values['program_list'] = program_list

        iframe_image = report_images(objsurvey.survey_id, domains)
        if iframe_image:
            if image_constants.is_production:
                iframe_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                    image_constants.image_dir + iframe_image
            else:
                iframe_image_path = image_constants.localhost + image_constants.metabase_images_localhost + iframe_image
            domain_report_values['iframe_image_path'] = iframe_image_path

        print("--------", domain_report_values)
        domain_report_list.append(domain_report_values)

    data = dict(zip(domain_name_list, domain_report_list))

    print(data)
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline;survey.pdf.pdf"

    html = render_to_string('survey_report.html', {'object': objsurvey,
                                                   'domain_index': data})
    print(set.BASE_DIR)
    HTML(string=html).write_pdf(response, stylesheets=report_css_path.stylesheet)
    return response



