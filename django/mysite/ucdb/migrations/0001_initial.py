# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user_id', models.AutoField(serialize=False, primary_key=True)),
                ('email', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('login_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField()),
                ('login_status', models.CharField(max_length=255, choices=[(b'0', b'login'), (b'1', b'logout')])),
                ('mediatype', models.IntegerField(null=True)),
                ('user_id', models.ForeignKey(to='ucdb.UserInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
