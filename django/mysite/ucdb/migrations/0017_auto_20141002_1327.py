# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0016_auto_20141002_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(help_text=b'User email (username for astakos authentication)', max_length=75, verbose_name=b'User email'),
        ),
    ]
