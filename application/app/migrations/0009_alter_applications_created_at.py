# Generated by Django 4.2.4 on 2024-10-11 21:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_applications_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 10, 11, 21, 57, 42, 411830, tzinfo=datetime.timezone.utc)),
        ),
    ]