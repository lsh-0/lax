# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-06 08:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0016_auto_20160905_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='datetime_submitted',
        ),
    ]