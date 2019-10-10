from django.shortcuts import render

import requests, re, json
import jwt

from utils.configuration import kobo_constants, metabase_constants
from utils.constants import kobo_form_constants, numeric_constants

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
    for response_entry in range(len(survey_form_data)):
        kobo_response_id = survey_form_data[response_entry]['_id']
        print(kobo_response_id)

        survey_response_id = survey_response.objects.filter(kobo_response_id=kobo_response_id, survey_id=surveyID).first()
        if not survey_response_id:
            print('survey response did not exist')
            survey_response(kobo_response_id=kobo_response_id, survey_id=surveyID).save()
            survey_response_id = survey_response.objects.last()
        else:
            print('survey response exists')
        list_of_keys = survey_form_data[response_entry].keys()
        survey_response_details = survey_response_detail.objects.filter(survey_response_id=survey_response_id).all()
        for question in questions:
            survey_question_response = ""
            survey_response_question_exists = survey_response_details.filter(survey_question_id=question).first()

            if not survey_response_question_exists:
                print('survey response exists but question does not exist')
                if question.question_name in survey_form_data[response_entry]:
                    print("direct question")
                    #print(question.question_name, " ",survey_form_data[response_entry][question.question_name])
                    survey_question_response = survey_form_data[response_entry][question.question_name]

                else:
                    print("question in group")
                    # pattern = r"(?<=/)\w+" + question.question_name
                    pattern = "/"+question.question_name+"$"
                    for key in list_of_keys:
                        questionname = re.search(pattern, key)
                        if questionname:
                            #print(pattern," ", survey_form_data[response_entry][key])
                            survey_question_response = survey_form_data[response_entry][key]

                optionID = survey_question_options.objects.filter(survey_question_id=question,
                                                                  option_name=survey_question_response).first()
                question_type = question.question_type
                if len(survey_question_response.split()) > numeric_constants.one and \
                        question_type in kobo_form_constants.questions_not_having_space:     # for select many questions
                    split_responses = survey_question_response.split()
                    for response in range(len(split_responses)):
                        survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                               survey_response_id=survey_response_id,
                                               survey_response_value=split_responses[response]).save()
                else:
                    survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                           survey_response_id=survey_response_id,
                                           survey_response_value=survey_question_response).save()

                print("question ID is ", question, " option id is", optionID)
                print("saved successfully")

        #print(question.question_name," ",[value for key, value in survey_form_data[response_entry].items() if question.question_name in key.lower()])
        print()

