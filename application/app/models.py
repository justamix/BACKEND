from django.db import models


class ApplicationClassrooms(models.Model):
    mm_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey('Classrooms', models.DO_NOTHING, blank=True, null=True)
    app = models.ForeignKey('Applications', models.DO_NOTHING, blank=True, null=True)
    finish_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'application_classrooms'


class Applications(models.Model):
    app_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    creator = models.IntegerField(blank=True, null=True)
    moderator = models.IntegerField(blank=True, null=True)
    event_date = models.DateTimeField(blank=True, null=True)
    event_name = models.CharField(max_length=100, blank=True, null=True)
    start_event_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=100, default='черновик',blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'applications'

    def GetClassrooms(self):
        arr = []
        for item in ApplicationClassrooms.objects.filter(app_id=self):
            a = item.classroom_id
            a.finish_time = item.finish_time
            arr.append(a)

        return arr


class Classrooms(models.Model):
    classroom_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    photo = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classrooms'