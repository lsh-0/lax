# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-05 17:46
from __future__ import unicode_literals

from django.db import migrations, models
from . import to_dict, turn_off_auto_now, turn_off_auto_now_add

def link_articles_to_versions(apps, schema_editor):
    Article = apps.get_model("publisher", "Article")
    ArticleVersion = apps.get_model("publisher", "ArticleVersion")

    turn_off_auto_now_add(ArticleVersion, "datetime_record_created")
    turn_off_auto_now(ArticleVersion, "datetime_record_updated")

    for av in ArticleVersion.objects.all():
        av.article = Article.objects.get(doi=av.doi)
        av.save()

class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0011_auto_20160405_1628'),
    ]

    operations = [

        #
        # drop fields from Article that now live in ArticleVersion
        # remove unique-together constraint on Article.version + Article.doi
        # add unique constraint to just Article.doi
        #

        migrations.AlterModelOptions(name='article', options={}),
        
        migrations.RemoveField(model_name='historicalarticle', name='datetime_published'),
        migrations.RemoveField(model_name='historicalarticle', name='version'),
        migrations.RemoveField(model_name='historicalarticle', name='status'),
        migrations.RemoveField(model_name='historicalarticle', name='slug'),
        migrations.RemoveField(model_name='historicalarticle', name='title'),
        
        migrations.AlterField(
            model_name='article',
            name='doi',
            field=models.CharField(help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalarticle',
            name='doi',
            field=models.CharField(db_index=True, help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255),
        ),
        migrations.AlterUniqueTogether(name='article', unique_together=set([])),
        migrations.RemoveField(model_name='article', name='datetime_published'),
        migrations.RemoveField(model_name='article', name='version'),
        migrations.RemoveField(model_name='article', name='status'),
        migrations.RemoveField(model_name='article', name='title'),
        migrations.RemoveField(model_name='article', name='slug'),

        #
        # add link to Article from ArticleVersion
        # manually update all links based on doi
        # finally, drop ArticleVersion.doi
        #
        
        migrations.AddField(
            model_name='articleversion',
            name='article',
            field=models.ForeignKey(default=1, on_delete=models.deletion.CASCADE, to='publisher.Article'),
            preserve_default=False,
        ),
        
        migrations.RunPython(link_articles_to_versions),

        migrations.AlterUniqueTogether(
            name='articleversion',
            unique_together=set([('article', 'version')]),
        ),

        migrations.RemoveField(model_name='ArticleVersion', name='doi'),

    ]

