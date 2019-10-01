from django.db import models
from django.utils.timezone import datetime
from django.contrib.auth.models import User


class survey(models.Model):
    survey_id = models.BigAutoField(primary_key=True)
    survey_name = models.CharField(max_length=255, null=False)
    survey_type_code_id = models.ForeignKey('common.code', null=False, blank=False, db_column='survey_type_code_id',
                                            related_name='fk_survey_type_code_id', on_delete=models.PROTECT)

    kobo_form_id = models.IntegerField(null=False,blank=False)
    location_id = models.ForeignKey('location.location', null=False, blank=False, db_column='location_id',
                                            related_name='fk_location_id', on_delete=models.PROTECT)
    publish_date = models.DateField(null=False)

    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_survey_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    modified_by = models.ForeignKey(User, null=True, db_column='modified_by', related_name='fk_survey_mby',
                                    on_delete=models.PROTECT)
    modified_on = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'sur_survey'
        get_latest_by = 'survey_id'


class survey_question(models.Model):
    survey_question_id = models.BigAutoField(primary_key=True)

    survey_id = models.ForeignKey('survey', db_column='survey_id', null=False, related_name='fk_survey_id',
                                  on_delete=models.PROTECT)

    section_id = models.CharField(max_length=255, null=True)
    question_name = models.CharField(max_length=255, null=False)
    question_label = models.CharField(max_length=255, null=False)

    domain_id = models.ForeignKey('domain.domain', db_column='domain_id', null=True, related_name='fk_survey_question_domain_id',
                                  on_delete=models.PROTECT)

    question_type = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'sur_survey_question'
        get_latest_by = 'survey_question_id'


class survey_question_options(models.Model):
    survey_question_options_id = models.BigAutoField(primary_key=True)

    survey_question_id = models.ForeignKey('survey_question', db_column='survey_question_id', null=False,
                                           related_name='fk_survey_question_id', on_delete=models.PROTECT)

    option_name = models.CharField(max_length=255, null=False)
    option_label = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'sur_survey_question_options'
        get_latest_by = 'survey_question_options_id'

