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
import json
from weasyprint import HTML, CSS
from django.http import HttpResponse
from weasyprint import HTML

from django.template.loader import render_to_string
from weasyprint.fonts import FontConfiguration
from operator import itemgetter
from cairosvg import svg2png
from bs4 import BeautifulSoup
# import cairo
# import rsvg


def get_svg(template_name):
    with open(template_name, 'r') as file:
        data = file.read()
        # print(data)
    soup = BeautifulSoup(data, 'html.parser')
    svg_string=[]
    svg_list = soup.find_all('svg')
    for svg in svg_list:
        svg_string.append(str(svg))
    print('#####################################################')
    # print(soup.prettify())
    # print(svg_string)
    return svg_string

def svg_convert(request):
    svg_string = get_svg('hello.html')
    print(svg_string)
    string_svg =[]
    for svg in svg_string:
        print("000000000000000000000000000000000000000000000000000000",str(svg))
        string_svg.append(str(svg))
        print("/////////////////", string_svg)
        svg_code = """<svg class="_2Gb1p m1" style="max-width: 550px; max-height: 550px;" viewbox="0 0 100 100">
         <g transform="translate(50,50)">
         <path class="" d="M0.508840086996788,-49.99741075061653A50,50 0 1,1 -49.9910665913336,0.9451248916675062L-29.990101830857306,0.7705791165151957A30,30 0 1,0 0.5088400869967876,-29.99568438568897Z" fill="#88BF4D" opacity="1"></path>
         <path class="" d="M-49.99994741349795,-0.07251653218338412A50,50 0 0,1 -0.5088400869967941,-49.99741075061653L-0.5088400869967913,-29.99568438568897A30,30 0 0,0 -29.998982653021653,-0.24706230733569653Z" fill="#7172AD" opacity="1"></path>
         </g>
         </svg>
        """
        svg2png(bytestring=svg_code,write_to='o2.png')

# parser = new DOMParser();
# doc = parser.parseFromString(stringContainingSVGSource, "image/svg+xml")

# def svg_convert(request):
#     img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640,480)
#
#     ctx = cairo.Context(img)
#     svg_string = get_svg('hello.html')
#     print(svg_string)
#     for svg in svg_string:
#
#         handle= rsvg.Handle(None, str(svg))
#         handle.render_cairo(ctx)
#         img.write_to_png("svg.png")



def survey_html(request,pk,template_name='survey_report.html'):
    objsurvey = get_object_or_404(survey, pk=pk)
    # Get list of distinct domain ids, applicable for the current survey
    distinct_domain_ids = survey_question.objects.values('domain_id').filter(survey_id=pk).distinct()

    # Get list of domain objects based on distinct domain list above
    domain_list = domain.objects.filter(domain_id__in=[item['domain_id'] for item in distinct_domain_ids])

    obj_location = location.objects.get(location_id=objsurvey.location_id.location_id)

    data_json = serializers.serialize('json', domain_list)
    data_list = json.loads(data_json)
    for item in data_list:
        index_value = response_views.get_domain_index(item, pk)
        item.update({"index": index_value})
        item.update({"location_id": obj_location.location_id})  # location id of conducted survey
    field_list = list(map(itemgetter('fields'), data_list))
    index = list(map(itemgetter('index'), data_list))
    domain_name_list = list(map(itemgetter('domain_name'), field_list))
    color = []
    for i in index:
        color_code = 'bg-flat-color-2'
        if float(i) < 25:
            color_code = 'bg-danger'
        elif float(i) >= 25 and float(i) < 50:
            color_code = 'bg-warning'
        elif float(i) >= 50 and float(i) < 75:
            color_code = 'bg-flat-color-2'
        else:
            color_code = 'bg-success'
        color.append(color_code)
    print(color)
    color_index = tuple(zip(index, color))

    domain_program_list = []
    for domains in domain_list:
        program_list = domain_program.objects.filter(domain_id=domains.domain_id).values('domain_program_id',
                                                                                         'program_name', 'description')
        for item in program_list:
            program_id = item['domain_program_id']
            if location_program.objects.filter(program_id=program_id, location_id=obj_location.location_id).exists():
                obj_location_program = location_program.objects.filter(program_id=program_id,
                                                                       location_id=obj_location.location_id). \
                    values('location_program_id', 'date_of_implementation', 'notes', 'location_id_id')
                before_after_images = {}
                for i in obj_location_program:
                    print(i)
                    if location_program_image.objects.filter(location_program_id=i['location_program_id']).exists():
                        before_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.before_images).values_list('image_name', flat=True)

                        for image in before_image_name:
                            if image_constants.is_production:
                                before_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image

                            else:
                                before_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image
                            print(before_image_path)
                            before_after_images['before'] = before_image_path
                        after_image_name = location_program_image.objects.filter \
                            (location_program_id=i['location_program_id'], \
                             image_type_code_id=numeric_constants.after_images).values_list('image_name', flat=True)
                        for image in after_image_name:
                            if image_constants.is_production:
                                after_image_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                                              image_constants.image_dir + image
                            else:
                                after_image_path = image_constants.localhost+image_constants.before_afterDirStatic + image
                            print(after_image_path)
                            before_after_images['after'] = after_image_path
                        i.update(before_after_images)
                    item.update(i)
            else:
                program_list.remove(item)
        domain_program_list.append(program_list)
    value_list = list(zip(color_index, domain_program_list))

    data = dict(zip(domain_name_list, value_list))
    return render(request, template_name, {'object': objsurvey,
                                             'domain_index':data})


def html_to_pdf_generation(request,pk): #weasyprint pdf generatiosurvey_idn common function
    objsurvey = get_object_or_404(survey, pk=pk)
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
        domain_program_list.append(program_list) # assign program list to respective domain
    value_list = list(zip(color_index,domain_program_list))

    data = dict(zip(domain_name_list, value_list))

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline;survey.pdf.pdf"

    html = render_to_string('survey_report.html', {'object': objsurvey,
                                             'domain_index':data})
    print(set.BASE_DIR)
    HTML(string=html).write_pdf(response, stylesheets=report_css_path.stylesheet)#, font_config=font_config, stylesheets=[CSS('/home/aishwarya/Project/Anarde/Anarde/village-development/code_base/static/theme/vendors/bootstrap/dist/css/bootstrap.min.css')])
    return response



