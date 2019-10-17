from django.shortcuts import render

import requests, re, json

from utils.configuration import kobo_constants, metabase_constants
from utils.constants import kobo_form_constants, numeric_constants

from common.models import code
from location.models import location
from domain.models import domain
from survey_form.models import survey, survey_question, survey_question_options
from .models import survey_response, survey_response_detail


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
            grp_name = survey_children[i]['name'].lower()
            print("****************")
            for j in range(len(survey_children[i]['children'])):
                get_kobo_questions_and_options(survey_children[i]['children'], j, surveyID, grp_name)

        else:
            print("----------------")
            get_kobo_questions_and_options(survey_children, i, surveyID)


def get_kobo_questions_and_options(survey_children, i, surveyID, grp_name=None):
    #print(grp_name)
    question_label = ""
    option_label = ""
    grp_key = ""
    question_weight = 0
    option_weight = 0
    if grp_name:
        domainname = re.search('_(.+?)_', grp_name)
        if domainname:
            grp_key = domainname.group(1)

    domainID = domain.objects.filter(kobo_group_key=grp_key).first()

    if survey_children[i]['type'] != 'group':
        if survey_children[i]['name'] not in kobo_form_constants.names_not_allowed:

            question_name = survey_children[i]['name'].lower()
            print(question_name)
            questionweight = re.search(numeric_constants.pattern_for_weights, question_name)
            if questionweight:
                question_weight = re.split(numeric_constants.pattern_for_weights, question_name)[1]
                question_name = re.split(numeric_constants.pattern_for_weights, question_name)[-1]
                print(question_weight)

            else:
                question_weight = 1

            #print('question weight ',question_weight)
            print("question name: ", question_name)
            survey_questionID = survey_question.objects.filter(survey_id=surveyID, question_name=question_name)

            if 'label' in survey_children[i].keys():
                print("question label ", survey_children[i]['label'])
                question_label = survey_children[i]['label']

            question_type = survey_children[i]['type']

            if survey_questionID:       # question exists so update
                print('question exists updating data  **************************************')
                if question_label:
                    survey_questionID.update(question_label=question_label)

                if domainID:
                    survey_questionID.update(domain_id=domainID, section_id=grp_name)

                if question_weight:
                    survey_questionID.update(question_weightage=question_weight)

            else:       # save as new question
                survey_question(survey_id=surveyID, section_id=grp_name, domain_id=domainID,
                                question_label=question_label, question_name=question_name,
                                question_type=question_type, question_weightage=question_weight).save()

            if question_type in kobo_form_constants.question_type_having_options:
                question_children = survey_children[i]['children']
                questionID = survey_question.objects.filter(survey_id=surveyID, question_name=question_name).first()

                for k in range(len(question_children)):
                    option_name = question_children[k]['name'].lower()
                    #print("options : ", option_name)
                    optionweight = re.search(numeric_constants.pattern_for_weights, option_name)
                    if optionweight:
                        option_weight = re.split(numeric_constants.pattern_for_weights, option_name)[1]
                        option_name = re.split(numeric_constants.pattern_for_weights, option_name)[-1]
                        print(option_weight, " ", option_name)
                    else:
                        option_weight = 1

                    if 'label' in question_children[k].keys():
                        option_label = question_children[k]['label']
                        print("option label ", option_label)

                    survey_optionID = survey_question_options.objects.filter(survey_question_id=questionID, option_name=option_name)

                    if survey_optionID:     # option exists for question
                        if option_weight:
                            survey_optionID.update(option_weightage=option_weight)

                        if option_label:
                            survey_optionID.update(option_label=option_label)

                    else:                   # save as new option for the question
                        survey_question_options(survey_question_id=questionID, option_name=option_name,
                                                option_label=option_label, option_weightage=option_weight).save()


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


def get_domain_index(item, survey_id):
    domain_name = item['fields']['kobo_group_key']
    print(domain_name)
    objdomain = domain.objects.filter(kobo_group_key=domain_name).first()
    questions_in_group = survey_question.objects.filter(domain_id=objdomain, survey_id=survey_id)
    survey_responseID = survey_response.objects.filter(survey_id=survey_id)
    if questions_in_group:
        weighted_sum = 0
        sum_of_question_weights = 0
        for question in questions_in_group:
            objsurvey_response = survey_response_detail.objects.filter(survey_response_id__in=survey_responseID,
                                                                       survey_question_id=question)

            if objsurvey_response.count() > numeric_constants.zero:     ## if no response exists for question skip
                question_weight = question.question_weightage

                sum_of_responses = 0
                number_of_responses = 0
                for response in objsurvey_response:
                    if response.survey_question_options_id:
                        option_weight = response.survey_question_options_id.option_weightage
                        sum_of_responses += option_weight
                        # print("option name is", response.survey_question_options_id.option_name,
                        #       "and weight is ", response.survey_question_options_id.option_weightage)
                    else:
                        sum_of_responses = 1
                    number_of_responses += 1
                #print("question is ",question, "and sum of response is ",sum_of_responses)
                #print("number of responses for question ",question.question_name," is ",number_of_responses)
                weighted_sum += (question_weight * sum_of_responses) / number_of_responses
                sum_of_question_weights += question_weight
        #print("weighted sum is ",weighted_sum)
        #print("sum of question weights is ", sum_of_question_weights)

        index = "%.2f" % ((weighted_sum / sum_of_question_weights)*100)
    else:
        index = 0

    print()
    return index

