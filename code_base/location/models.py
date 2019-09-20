from django.db import models
from django.utils.timezone import datetime
from  django.contrib.auth.models import User

# Create your models here.
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

    # def __str__(self):
    #     return "%s" % (self.location_name)


    class Meta:
        db_table = 'loc_location'
        get_latest_by = 'location_id'

