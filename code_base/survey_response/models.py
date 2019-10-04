from django.db import models


class survey_response(models.Model):
    survey_response_id = models.BigAutoField(primary_key=True)

    survey_id = models.ForeignKey('survey_form.survey', db_column='survey_id', null=False, related_name='fk_kobo_response_survey_id',
                                 on_delete=models.PROTECT)

    kobo_response_id = models.IntegerField(null=False, blank=True)

    class Meta:
        db_table = 'sur_survey_response'
        get_latest_by = 'survey_response_id'


class survey_response_detail(models.Model):

    survey_reponse_detail_id = models.BigAutoField(primary_key=True)

    survey_response_id = models.ForeignKey('survey_response', db_column='survey_response_id', null=False,
                                  related_name='fk_survey_response_id', on_delete=models.PROTECT)

    survey_question_id = models.ForeignKey('survey_form.survey_question', db_column='survey_question_id', null=False,
                                           related_name='fk_survey_response_question_id', on_delete=models.PROTECT)

    survey_question_options_id = models.ForeignKey('survey_form.survey_question_options', db_column='survey_question_options_id',
                                                   null=True, related_name='fk_survey_response_details_question_options_id', on_delete=models.PROTECT)

    survey_response_value = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'sur_survey_response_detail'
        get_latest_by = 'survey_response_detail_id'