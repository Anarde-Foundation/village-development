from django.db import models
from django.utils.timezone import datetime
from django.contrib.auth.models import User
from location.models import location_program

class funder(models.Model):
    funder_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, null=False, db_column='user_id', related_name='fk_funder_uid',
                                   on_delete=models.PROTECT)

    organization_name = models.CharField(max_length=255, null=False)

    funding_amount = models.IntegerField(null=True, blank=True)
    funding_date = models.DateField(null=False)

    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_funder_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    modified_by = models.ForeignKey(User, null=True, db_column='modified_by', related_name='fk_funder_mby',
                                    on_delete=models.PROTECT)
    modified_on = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'fun_funder'
        get_latest_by = 'funder_id'


class funder_program(models.Model):
    funder_program_id = models.BigAutoField(primary_key=True)

    funder_id = models.ForeignKey('funder', null=False, blank=False, db_column='funder_id',
                                    related_name='fk_funder_id', on_delete=models.PROTECT)

    location_program_id = models.ForeignKey(location_program, null=False, db_column='location_program_id',
                                            related_name='fk_loc_program_id', on_delete=models.PROTECT)

    funding_amount = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = 'fun_funder_program'
        get_latest_by = 'funder_program_id'