# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-06 10:18


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("publisher", "0017_remove_article_datetime_submitted")]

    operations = [
        migrations.RemoveField(model_name="articlecorrection", name="article"),
        migrations.DeleteModel(name="ArticleCorrection"),
    ]
