# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0004_delete_old_artifact_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fir_artifacts', '0002_create_artifacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('subject', models.CharField(max_length=256)),
                ('body', models.TextField()),
                ('status', models.CharField(default=b'Open', max_length=20, choices=[(b'O', b'Open'), (b'A', b'Archived'), (b'D', b'Deleted')])),
                ('artifacts', models.ManyToManyField(related_name='articles', to='fir_artifacts.Artifact')),
                ('category', models.ForeignKey(to='incidents.IncidentCategory')),
                ('incidents', models.ManyToManyField(to='incidents.Incident')),
                ('opened_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('access_articles', 'Can access articles'), ('modify_articles', 'Can modify articles')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=200)),
                ('article', models.ForeignKey(related_name='attribute_set', to='fir_articles.Article')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleComments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('comment', models.TextField()),
                ('article', models.ForeignKey(related_name='comments_set', to='fir_articles.Article')),
                ('opened_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
