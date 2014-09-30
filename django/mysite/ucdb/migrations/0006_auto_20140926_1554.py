# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0005_auto_20140926_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogin',
            name='mediatype',
            field=models.IntegerField(null=True, verbose_name=b'Media Type'),
        ),
    ]
