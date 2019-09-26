from django.db import models
from django.utils.timezone import datetime
from  django.contrib.auth.models import User

# Create your models here.
class domain(models.Model):
    domain_id = models.BigAutoField(primary_key=True)
    domain_name = models.CharField(max_length=255, null=False)
    kobo_group_key = models.CharField(max_length=255, null=False)

    description = models.TextField(null=True, blank=True)


    created_by = models.ForeignKey(User, null=True, db_column='created_by', related_name='fk_domain_cby',
                                   on_delete=models.PROTECT)
    created_on = models.DateTimeField(default=datetime.now)

    modified_by = models.ForeignKey(User, null=True, db_column='modified_by', related_name='fk_domain_mby',
                                    on_delete=models.PROTECT)
    modified_on = models.DateTimeField(default=datetime.now)

    # def __str__(self):
    #     return "%s" % (self.location_name)


    class Meta:
        db_table = 'com_domain'
        get_latest_by = 'domain_id'


