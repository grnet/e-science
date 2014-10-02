# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0015_auto_20141002_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='uuid',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(help_text=b'User email (username for astakos authentication)', max_length=75, null=True, verbose_name=b'User email'),
            preserve_default=True,
        ),
    ]
