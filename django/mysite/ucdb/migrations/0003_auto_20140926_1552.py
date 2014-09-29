# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0002_auto_20140926_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogin',
            name='login_id',
            field=models.AutoField(serialize=False, verbose_name=b'Login ID', primary_key=True),
        ),
    ]
