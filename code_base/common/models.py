from django.db import models

# Create your models here.
class code_group(models.Model):
    code_group_id = models.IntegerField(primary_key=True)
    code_group_name = models.CharField(max_length=255, null=False, unique=True)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'com_code_group'
        get_latest_by = 'code_group_name'


class code(models.Model):
    code_id = models.IntegerField(primary_key=True)
    code_group = models.ForeignKey('code_group', db_column='code_group_id', null=False, related_name='fk_code_code_group_id',
                                   on_delete=models.PROTECT)
    code_name = models.CharField(max_length=255, null=False)
    display_order = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=255, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def natural_key(self):
        return self.code_name

    def __str__(self):
        return "%s" % (self.code_name)

    class Meta:
        db_table = 'com_code'
        get_latest_by = 'code_name'
