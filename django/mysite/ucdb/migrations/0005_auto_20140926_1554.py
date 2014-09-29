# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0004_auto_20140926_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogin',
            name='login_status',
            field=models.CharField(max_length=255, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')]),
        ),
    ]
