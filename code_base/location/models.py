from django.db import models
from django.utils.timezone import datetime
from  django.contrib.auth.models import User
from domain.models import domain, domain_program

class location(models.Model):
    location_id = models.BigAutoField(primary_key=True)
    location_name = models.CharField(max_length=255, null=False)
    date_of_intervention = models.DateField(null=False)
    exit_date = models.DateField(null=True)
    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_location_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    modified_by = models.ForeignKey(User, null=True, db_column='modified_by', related_name='fk_location_mby',
                                    on_delete=models.PROTECT)
    modified_on = models.DateTimeField(default=datetime.now)

    def natural_key(self):
        return self.location_name

    def __str__(self):
        return "%s" % (self.location_name)


    class Meta:
        db_table = 'loc_location'
        get_latest_by = 'location_id'


class location_program(models.Model):
    location_program_id = models.BigAutoField(primary_key=True)
    location_id = models.ForeignKey('location.location', null=False, blank=False, db_column='location_id',
                                    related_name='fk_location_pid', on_delete=models.PROTECT)
    program_id = models.ForeignKey(domain_program, null=False, db_column='program_id', related_name='fk_program_lid',
                                  on_delete=models.PROTECT)

    date_of_implementation = models.DateField(null=False)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_location_program_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    modified_by = models.ForeignKey(User, null=True, db_column='modified_by', related_name='fk_location_program_mby',
                                    on_delete=models.PROTECT)
    modified_on = models.DateTimeField(default=datetime.now)


    def natural_key(self):
        return self.program_id.program_name

    def __str__(self):
        return "%s" % (self.program_id.program_name)

    class Meta:
        db_table = 'loc_location_program'
        get_latest_by = 'location_program_id'


class location_program_image(models.Model):
    location_program_image_id = models.BigAutoField(primary_key=True)
    image_name = models.CharField(max_length=255, null=False)
    image_type_code_id = models.ForeignKey('common.code', null=False, blank=False, db_column='image_type_code_id',
                                            related_name='fk_image_type_code_id', on_delete=models.PROTECT)

    location_program_id = models.ForeignKey('location_program', null=False, blank=False, db_column='location_program_id',
                                            related_name='fk_location_program_id', on_delete=models.PROTECT)

    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_image_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'loc_location_program_image'
        get_latest_by = 'location_program_image_id'
