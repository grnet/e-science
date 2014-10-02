# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0013_auto_20141002_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='uuid',
            field=models.CharField(help_text=b'Universally unique identifier (for astakos authentication)', unique=True, max_length=255, verbose_name=b'UUID'),
        ),
    ]
