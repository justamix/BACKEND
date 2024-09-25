from django.db import models


class ApplicationClassroom(models.Model):
    mm_id = models.IntegerField(primary_key=True)
    classroom = models.ForeignKey('Classrooms', models.DO_NOTHING, blank=True, null=True)
    app = models.ForeignKey('Applications', models.DO_NOTHING, blank=True, null=True)
    finish_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'application_classroom'


class Applications(models.Model):
    app_id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField()
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey('Users', models.DO_NOTHING, db_column='creator', blank=True, null=True)
    moderator = models.ForeignKey('Users', models.DO_NOTHING, db_column='moderator', related_name='applications_moderator_set', blank=True, null=True)
    event_date = models.DateTimeField()
    event_name = models.CharField(max_length=100, blank=True, null=True)
    start_event_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'applications'


class Classrooms(models.Model):
    classroom_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    photo = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classrooms'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=100)
    mail = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    admin = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'