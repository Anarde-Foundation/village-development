from django.shortcuts import render

import requests, re, json

from utils.configuration import kobo_constants
from utils.constants import kobo_form_constants

from common.models import code
from location.models import location
from domain.models import domain
from survey_form.models import survey, survey_question, survey_question_options
from .models import survey_response,survey_response_detail


def pull_kobo_response_data(surveyID):

    print(surveyID)
    kobo_form_id = surveyID.kobo_form_id
    data_link = kobo_constants.kobo_data_link + "/" + str(kobo_form_id)
    print(data_link)
    survey_form_data = requests.get(data_link, headers={'Authorization': kobo_constants.authorization_token}).json()
    questions = survey_question.objects.filter(survey_id=surveyID).all()
    print(len(survey_form_data))
    for i in range(len(survey_form_data)):
        kobo_response_id = survey_form_data[i]['_id']
        print(kobo_response_id)

        survey_response_id = survey_response.objects.filter(kobo_response_id=kobo_response_id, survey_id=surveyID).first()
        if not survey_response_id:
            survey_response(kobo_response_id=kobo_response_id, survey_id=surveyID).save()
            survey_response_id = survey_response.objects.last()
            list_of_keys = survey_form_data[i].keys()
            for question in questions:
                survey_question_response = ""
                #survey_questionID = question.survey_question_id
                if question.question_name in survey_form_data[i]:
                    print("direct question")
                    #print(question.question_name, " ",survey_form_data[i][question.question_name])
                    survey_question_response = survey_form_data[i][question.question_name]

                else:
                    print("question in group")
                    # pattern = r"(?<=/)\w+" + question.question_name
                    pattern = "/"+question.question_name+"$"
                    for key in list_of_keys:
                        questionname = re.search(pattern, key)
                        if questionname:
                            #print(pattern," ", survey_form_data[i][key])
                            survey_question_response = survey_form_data[i][key]

                optionID = survey_question_options.objects.filter(survey_question_id=question,
                                                                  option_name=survey_question_response).first()

                if len(survey_question_response.split()) == 1 :     # for select many questions
                    survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                           survey_response_id=survey_response_id,
                                           survey_response_value=survey_question_response).save()
                else:
                    split_response = survey_question_response.split()
                    for i in range(len(split_response)):
                        survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                               survey_response_id=survey_response_id,
                                               survey_response_value=split_response[i]).save()

                print("question ID is ", question, " option id is", optionID)
                print("saved successfully")
        else:
            print("response exists")
            #print(question.question_name," ",[value for key, value in survey_form_data[i].items() if question.question_name in key.lower()])
        print()