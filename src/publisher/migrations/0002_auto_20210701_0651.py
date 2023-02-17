# Generated by Django 2.2.24 on 2021-07-01 06:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("publisher", "0001_squashed_0009_auto_20200910_0409"),
    ]

    operations = [
        migrations.AddField(
            model_name="articleevent",
            name="uri",
            field=models.URLField(
                blank=True,
                help_text="location of event, if any",
                max_length=2000,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="articleevent",
            name="event",
            field=models.CharField(
                choices=[
                    ("date-preprint", "preprint published"),
                    ("date-qc", "quality check date"),
                    ("date-decision", "decision date"),
                    ("date-xml-received", "received date (XML)"),
                    ("date-xml-accepted", "accepted date (XML)"),
                    ("datetime-action-ingest", "'ingest' event"),
                    ("datetime-action-publish", "'publish' event"),
                ],
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="articleevent",
            name="value",
            field=models.CharField(
                blank=True,
                help_text="a value, if any, associated with this event",
                max_length=255,
                null=True,
            ),
        ),
    ]
