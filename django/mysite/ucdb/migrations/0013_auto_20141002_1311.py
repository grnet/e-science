# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0012_auto_20141002_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='uuid',
            field=models.CharField(help_text=b'User email (username for astakos authentication)', unique=True, max_length=255, verbose_name=b'User email'),
        ),
    ]
