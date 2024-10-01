from django.db import models
from django.contrib.auth.models import User

class ApplicationClassrooms(models.Model):
    mm_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey('Classrooms', models.DO_NOTHING, blank=True, null=True)
    app = models.ForeignKey('Applications', models.DO_NOTHING, blank=True, null=True)
    finish_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'application_classrooms'


class Applications(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )
    app_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    creator = models.IntegerField(blank=True, null=True)
    moderator = models.IntegerField(blank=True, null=True)
    event_date = models.DateTimeField(blank=True, null=True)
    event_name = models.CharField(max_length=100, blank=True, null=True)
    start_event_time = models.TimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1,blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'applications'

    def GetClassrooms(self):
        return ApplicationClassrooms.objects.filter(app=self).values_list('classroom', flat=True)


class Classrooms(models.Model):
    classroom_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    photo = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'classrooms'