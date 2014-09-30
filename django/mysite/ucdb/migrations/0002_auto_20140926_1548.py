# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.CharField(max_length=255, verbose_name=b"User's email"),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='user_id',
            field=models.AutoField(serialize=False, verbose_name=b'User ID', primary_key=True),
        ),
    ]
