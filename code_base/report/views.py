import inspect

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
import json
import jwt
from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from base64 import b64encode
from lxml import etree
import xml.etree.ElementTree as ET
from io import BytesIO
from pprint import pprint
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from weasyprint.fonts import FontConfiguration
from operator import itemgetter

def show_weasy_html_page(request):
    return render(request, 'hello.html')

def weasy_embed_svg(html, htmlAsString):
    print ('=========================================================================================in weasy embed svg')

    """For the child of nvd3 nodes (svg) munge them into b64encoded data
            as a workaround for https://github.com/Kozea/WeasyPrint/issues/75"""

    # tree = etree.ElementTree.parse(html)
    root = ET.fromstring('<data><rank>1</rank></data>')#html.etree_element[0]
    pprint(inspect.getmembers(root), indent=2)
    svgs = root.findall('.//svg') #//body//svg
    print("svgs  is  ================================ ")
    # pprint(inspect.getmembers(svgs), indent=2)
    print(svgs)

    for svg in svgs:
        print("in svg")
        child = svg.getchildren()[0]
        encoded = b64encode(etree.tostring(child)).decode()
        encoded_data = "data:image/svgxml;charset=utf-8;base64," + encoded
        encoded_child = etree.fromstring('<img src="%s"/>' % encoded_data)
        svg.replace(child, encoded_child)

    return html


def pdf_generation(request):
    # HTML('http://127.0.0.1:8000/report/weasy_html_page').write_pdf('weasy_html_page.pdf')
    print('****************************************************************************************in pdf generation')
    html = HTML('http://127.0.0.1:8000/report/weasy_html_page')
    print(html)
    # htmlBytes = BytesIO(html.encode("ISO-8859-1"))
    # htmlWithsvg = weasy_embed_svg(html)
    # rendered = htmlWithsvg.render()

    mysvg = ' <svg class="_2Gb1p m1" viewBox="0 0 100 100" style="max-width: 550px; max-height: 550px;"><g transform="translate(50,50)"><path d="M0.508840086996788,-49.99741075061653A50,50 0 1,1 -14.590143219827354,47.82392414707231L-8.559189777869605,28.75309149198417A30,30 0 1,0 0.5088400869967876,-29.99568438568897Z" fill="#98D9D9" opacity="1" class=""></path><path d="M-15.560459878526562,47.51707154664274A50,50 0 0,1 -0.5088400869967941,-49.99741075061653L-0.5088400869967913,-29.99568438568897A30,30 0 0,0 -9.529506436568814,28.4462388915546Z" fill="#F2A86F" opacity="1" class=""></path></g></svg>'
    myhtml = '<html><body>Hey there! <br/>' + mysvg + '</body></html>'
    htmlWithsvg = weasy_embed_svg(HTML(string=myhtml, base_url='http://127.0.0.1:8000/'), myhtml)
    rendered = htmlWithsvg.render()
    rendered.write_pdf('weasy_html_page.pdf')

    location_list = location.objects.all()
    data = serializers.serialize('json', location_list)
    return HttpResponse(data, content_type='application/json')

def survey_html(request,pk,template_name='temp.html'):
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
    res = list(map(itemgetter('fields'), data_list))
    index = list(map(itemgetter('index'), data_list))
    res1 = list(map(itemgetter('domain_name'), res))
    color = []
    for i in index:
        color_code = 'bg-flat-color-2'
        if float(i) < 25 :
            color_code = 'bg-danger'
        elif  float(i) >= 25 and float(i) < 50 :
            color_code = 'bg-warning'
        elif float(i) >= 50  and float(i) < 75:
            color_code = 'bg-flat-color-2'
        else:
            color_code = 'bg-success'
        color.append(color_code)
    print(color)
    color_index = tuple(zip(index, color))
    data = dict(zip(res1, color_index))
    return render(request, template_name, {'object': objsurvey,
                                             'domain_index':data})


def html_to_pdf_generation(request,pk): #weasyprint pdf generatiosurvey_idn common function
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
    res = list(map(itemgetter('fields'), data_list))
    index = list(map(itemgetter('index'), data_list))
    res1 = list(map(itemgetter('domain_name'), res))
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
    data = dict(zip(res1, color_index))
 
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline;survey.pdf.pdf"

    html = render_to_string('temp.html', {'object': objsurvey,
                                             'domain_index':data})
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config, stylesheets=[CSS('/home/aishwarya/Project/Anarde/Anarde/village-development/code_base/static/theme/vendors/bootstrap/dist/css/bootstrap.min.css')])
    return response






# Create your views here.

def get_survey_question_list_for_pdf(request, pk):
    survey_questions_list = survey_question.objects.filter(survey_id = pk )
    data = serializers.serialize('json', survey_questions_list)
    return HttpResponse(data, content_type='application/json')


def InvoicePDFView(request,pk):
    #Retrieve data or whatever you need
    # obj_domain = domain.objects.get(pk=domain_id)
    obj_survey = survey.objects.get(survey_id = pk)
    obj_survey_question = get_survey_question_list_for_pdf(request,pk)
    return render_to_pdf(
            'generate_pdf.html',
            {
                'pagesize':'A4',
                'object': obj_survey,
                'obj_question': obj_survey_question,

            }
        )

def show_domainwise_metabase_graph(request, survey_id, domain_id):
    # Get domain object
    # objDomain = get_object_or_404(domain, pk=domain_id)
    try:
        objDomain = domain.objects.get(pk = domain_id)
    except domain.DoesNotExist:
        objDomain = None

    if (objDomain == None or objDomain.metabase_dashboard_id == None):
        # responseData = {}
        # responseData['iframeUrl'] = ''
        return None
    else:
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
    #     responseData = {}
    #     responseData['iframeUrl'] = iframeUrl
    #
    # data = json.dumps(responseData) #{'iframeUrl': iframeUrl}
    # return HttpResponse(data, content_type='application/json')

def domain_graphs_pdf(request,pk,domain_id):
    iframeUrl = show_domainwise_metabase_graph(request, pk, domain_id)
    print(iframeUrl)
    return render_to_pdf(
        'Metabase.html',
        {
            'iframeUrl': iframeUrl,
        }
    )