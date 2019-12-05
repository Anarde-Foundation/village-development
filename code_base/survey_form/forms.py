import re
import requests

from utils.configuration import kobo_constants, metabase_constants, image_constants
from utils.constants import kobo_form_constants, numeric_constants, code_group_names
from .models import survey

from django.forms import ModelForm
from django import forms
from django.utils.timezone import datetime
from location.models import location, location_program
from common.models import code, code_group

def get_kobo_forms(surveyID=None):
    base_response = requests.get(kobo_constants.kobo_form_link,
                                 headers={'Authorization': kobo_constants.authorization_token}).json()
    list_res = []
    for i in range(len(base_response)):
        surveyObj = survey.objects.filter(kobo_form_id=base_response[i]['formid']).first()
        if surveyObj:
            survey_ID = surveyObj.survey_id
            if survey_ID == surveyID:
                print(base_response[i]['formid'], " ", base_response[i]['title'], " ", base_response[i]['date_created'])
                match = re.search(r'\d{4}-\d{2}-\d{2}', base_response[i]['date_created'])
                date = datetime.strptime(match.group(), '%Y-%m-%d').date()
                res = (base_response[i]['formid'], base_response[i]['title'] + " (" + str(date) + ")")
                list_res.append(res)

        else:
            print(base_response[i]['formid'], " ", base_response[i]['title'], " ", base_response[i]['date_created'])
            match = re.search(r'\d{4}-\d{2}-\d{2}', base_response[i]['date_created'])
            date = datetime.strptime(match.group(), '%Y-%m-%d').date()
            res = (base_response[i]['formid'], base_response[i]['title'] + " (" + str(date) + ")")
            list_res.append(res)

    return sorted(tuple(list_res), reverse=True)


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
    kobo_form_id = forms.ChoiceField(required=True, label='Select Kobo Form', choices=kobo_forms)

    survey_name = forms.CharField(required=True, label='Survey name', max_length=100)

    code_group_id = code_group.objects.filter(code_group_id=code_group_names.survey_type)
    code_queryset = code.objects.filter(code_group_id=code_group_id[0])
    survey_type_code_id = forms.ModelChoiceField(queryset=code_queryset, empty_label='Select an Option',
                                                 label='Select Survey Type', required=True)

    def __init__(self, *args, **kwargs):
        surveyID = kwargs.pop('surveyID')
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['kobo_form_id'] = forms.ChoiceField(choices=get_kobo_forms(surveyID))

    class Meta:
        model = survey
        fields = ['location_id', 'kobo_form_id', 'survey_name', 'survey_type_code_id']


# location program list form
class LocationProgram_Form(ModelForm):
    YEARS = [x for x in range(1990, 2021)]

    date_of_implementation = forms.DateField(required=True,
                                           label='Date of implementation', initial= datetime.now(),
                                           widget=forms.SelectDateWidget(empty_label="", years=YEARS))

    before_image_upload = forms.ImageField(required=False, widget=forms.widgets.ClearableFileInput())
    after_image_upload = forms.ImageField(required=False, widget=forms.widgets.ClearableFileInput())
    notes = forms.CharField(required=True, label='notes')
    class Meta:
        model = location_program
        fields = ['date_of_implementation', 'before_image_upload', 'after_image_upload', 'notes']
