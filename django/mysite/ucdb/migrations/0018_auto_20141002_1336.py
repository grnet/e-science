# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0017_auto_20141002_1327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='email',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='uuid',
            field=models.CharField(default=b'', help_text=b'Universally unique identifier (for astakos authentication)', unique=True, max_length=255, verbose_name=b'UUID'),
            preserve_default=True,
        ),
    ]
