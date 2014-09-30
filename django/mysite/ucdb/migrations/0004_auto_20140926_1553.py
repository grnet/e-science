# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0003_auto_20140926_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogin',
            name='action_date',
            field=models.DateTimeField(verbose_name=b'Action Date'),
        ),
    ]
