# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-16 11:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0029_auto_20161014_1533'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articleversion',
            options={'ordering': ('datetime_published',)},
        ),
    ]
