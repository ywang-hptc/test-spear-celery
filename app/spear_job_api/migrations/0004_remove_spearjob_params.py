# Generated by Django 5.1.6 on 2025-03-06 00:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spear_job_api', '0003_spearjob_args_spearjob_kwargs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spearjob',
            name='params',
        ),
    ]
