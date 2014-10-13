# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_escience', '0003_auto_20141003_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogin',
            name='login_status',
            field=models.CharField(help_text=b'Login/Logout status of the user', max_length=10, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')]),
        ),
    ]
