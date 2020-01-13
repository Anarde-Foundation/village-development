from django.shortcuts import render

import requests, re, json, os

from utils.configuration import kobo_constants, metabase_constants, image_constants, aws_bucket_constants
from utils.constants import kobo_form_constants, numeric_constants

from common.models import code
from location.models import location
from domain.models import domain
from survey_form.models import survey, survey_question, survey_question_options
from .models import survey_response, survey_response_detail
from django.utils.timezone import datetime
import boto3


def pull_kobo_form_data(surveyID):

    print(surveyID)
    kobo_form_id = surveyID.kobo_form_id
    data_link = kobo_constants.kobo_form_link+ "/" + str(kobo_form_id) + kobo_form_constants.data_format
    print(data_link)
    survey_form_data = requests.get(data_link, headers={'Authorization': kobo_constants.authorization_token}).json()
    # print(json.dumps(survey_data, indent=4))
    survey_children = survey_form_data['children']
    print("survey_name: ", survey_form_data['title'])
    error_log = []
    for i in range(len(survey_children)):
        if survey_children[i]['type'] == 'group':
            grp_name = survey_children[i]['name'].lower()
            print("****************")
            for j in range(len(survey_children[i]['children'])):
                error_log = get_kobo_questions_and_options(survey_children[i]['children'], j, surveyID, error_log, grp_name)

        else:
            print("----------------")
            error_log = get_kobo_questions_and_options(survey_children, i, surveyID, error_log)

    return error_log


def get_kobo_questions_and_options(survey_children, i, surveyID, error_log, grp_name=None):
    # print(grp_name)
    question_label = ""
    option_label = ""
    grp_key = ""
    question_weight = 0
    option_weight = 0
    domainID = 0
    if grp_name:
        domainname = re.search('_(.+?)_', grp_name)
        if domainname:
            grp_key = domainname.group(1)
            if not domain.objects.filter(kobo_group_key=grp_key):
                error_log.append('group name ' + grp_name + ' not in domain')
        else:
            if grp_name != 'meta':
                error_log.append('group name ' + grp_name + ' not in domain')
    domainID = domain.objects.filter(kobo_group_key=grp_key).first()

    if survey_children[i]['type'] != 'group':
        if survey_children[i]['name'] not in kobo_form_constants.names_not_allowed:

            question_name = survey_children[i]['name'].lower()
            questionweight = re.search(numeric_constants.pattern_for_weights, question_name)
            if questionweight:
                question_weight = re.split(numeric_constants.pattern_for_weights, question_name)[1]
                question_name = re.split(numeric_constants.pattern_for_weights, question_name)[-1]
                #print(question_weight)

            else:
                question_weight = 1
                error_log.append('Question: ' + question_name + ' has no weight assigned. Default weight 1 assigned')

            # print('question weight ',question_weight)
            # print("question name: ", question_name)
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
                    optionweight = re.search(numeric_constants.pattern_for_weights, option_name)
                    if optionweight:
                        option_weight = re.split(numeric_constants.pattern_for_weights, option_name)[1]
                        option_name = re.split(numeric_constants.pattern_for_weights, option_name)[-1]
                        print(option_weight, " ", option_name)
                    else:
                        option_weight = 1
                        error_log.append(
                            'Question: ' + question_name + ' having option: '+ option_name +
                            ' has no weight assigned. Default weight 1 assigned')

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

    print(error_log)
    return error_log


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

                for key in list_of_keys:
                    new_key = key.lower()
                    if new_key in kobo_form_constants.names_not_allowed:
                        continue
                    # print(question.question_name, " ",new_key)
                    if question.question_name == new_key:
                        print("direct question")
                        # print(question.question_name, " ",survey_form_data[response_entry][question.question_name])
                        survey_question_response = survey_form_data[response_entry][key]

                    else:
                        pattern = question.question_name+"$"
                        questionname = re.search(pattern, new_key)
                        if questionname:
                            print("question in group - ", key)
                            #print(pattern," ", survey_form_data[response_entry][key])
                            survey_question_response = survey_form_data[response_entry][key]

                if survey_question_response:
                    survey_question_response_lower = survey_question_response.lower()
                    optionweight = re.search(numeric_constants.pattern_for_weights, survey_question_response_lower)
                    if optionweight:
                        survey_question_response_lower = re.split(numeric_constants.pattern_for_weights,
                                                                  survey_question_response_lower)[-1]

                    optionID = survey_question_options.objects.filter(survey_question_id=question,
                                                                      option_name=survey_question_response_lower).first()
                    question_type = question.question_type

                    if len(survey_question_response.split()) > numeric_constants.one and \
                            question_type in kobo_form_constants.questions_not_having_space:     # for select many questions

                        split_responses = survey_question_response_lower.split()
                        for response in range(len(split_responses)):
                            survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                                   survey_response_id=survey_response_id,
                                                   survey_response_value=split_responses[response]).save()
                    else:
                        survey_response_detail(survey_question_id=question, survey_question_options_id=optionID,
                                               survey_response_id=survey_response_id,
                                               survey_response_value=survey_question_response_lower).save()

                    print("question ID is ", question, " option id is", optionID)
                    print("saved successfully")
                else:
                    print("Empty response")

        #print(question.question_name," ",[value for key, value in survey_form_data[response_entry].items() if question.question_name in key.lower()])
        print()


def get_domain_index(domain_name, survey_id):
    print(domain_name)
    objdomain = domain.objects.filter(kobo_group_key=domain_name).first()
    questions_in_group = survey_question.objects.filter(domain_id=objdomain, survey_id=survey_id)
    survey_responseID = survey_response.objects.filter(survey_id=survey_id)
    index = 0
    if questions_in_group:
        weighted_sum = 0
        sum_of_question_weights = 0
        for question in questions_in_group:
            objsurvey_response = survey_response_detail.objects.filter(survey_response_id__in=survey_responseID,
                                                                       survey_question_id=question)

            if objsurvey_response.count() > numeric_constants.zero:     # if no response exists for question skip
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
                # print("question is ",question, "and sum of response is ",sum_of_responses)
                # print("number of responses for question ",question.question_name," is ",number_of_responses)
                weighted_sum += (question_weight * sum_of_responses) / number_of_responses
                sum_of_question_weights += question_weight
        # print("weighted sum is ",weighted_sum)
        # print("sum of question weights is ", sum_of_question_weights)

        if sum_of_question_weights > numeric_constants.zero:
            index = "%.2f" % ((weighted_sum / sum_of_question_weights)*100)

    return index


# function to save images directly to s3 bucket
def move_to_s3(image, imageName, image_dir):

    session = boto3.Session(
        aws_access_key_id=aws_bucket_constants.aws_access_key_id,
        aws_secret_access_key=aws_bucket_constants.aws_secret_access_key,
        region_name=aws_bucket_constants.region_name
    )

    s3 = session.resource('s3')
    bucket = s3.Bucket(aws_bucket_constants.bucket_name)

    path_on_bucket = image_dir+imageName
    print(path_on_bucket)
    bucket.put_object(Key=path_on_bucket, Body=image, ContentType='image/jpeg')

                      #ACL="'private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control'")


# function to save images
def save_images(image, type_image):

    if image is not None:
        imageName, fileLocation, static_path = createImageName(image, type_image)
        print("location is ", fileLocation, " and image name is ", imageName)
        print("static path is ", static_path)

        if image_constants.is_production:
            move_to_s3(image, imageName, image_constants.image_dir)
            print('successfully stored in s3 bucket')
        else:
            with open(fileLocation, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

        return static_path, imageName


# function to construct image name
def createImageName(image, type_image):

    currentDateTime = datetime.now().strftime("%y%m%d%H%M%S%f")
    tempFileName, fileExtension = os.path.splitext(image.name)

    if type_image == image_constants.image_type_before:
        imageName = (r"before_" + currentDateTime + fileExtension)
    else:
        imageName = (r"after_" + currentDateTime + fileExtension)

    fileLocation = str(image_constants.before_afterDir) + str(imageName)
    if image_constants.is_production:
        static_path = aws_bucket_constants.s3_bucket_path + aws_bucket_constants.bucket_name + "/" + \
                      image_constants.image_dir + str(imageName)
        print(static_path)
    else:
        static_path = image_constants.before_afterDirStatic + str(imageName)
    print(static_path)
    return imageName, fileLocation, static_path
