# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("publisher", "0006_auto_20170531_0118")]

    operations = [
        migrations.AlterField(
            model_name="articleevent",
            name="event",
            field=models.CharField(
                choices=[
                    ("date-qc", "quality check date"),
                    ("date-decision", "decision date"),
                    ("date-xml-received", "received date (XML)"),
                    ("date-xml-accepted", "accepted date (XML)"),
                    ("datetime-action-ingest", "'ingest' event"),
                    ("datetime-action-publish", "'publish' event"),
                ],
                max_length=25,
            ),
        )
    ]
