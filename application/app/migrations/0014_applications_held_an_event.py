# Generated by Django 4.2.4 on 2024-11-07 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_applications_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='applications',
            name='held_an_event',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
