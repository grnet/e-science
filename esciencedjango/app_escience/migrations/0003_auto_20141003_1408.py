# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_escience', '0002_auto_20141003_1255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clusterinfo',
            options={'verbose_name': 'Cluster'},
        ),
        migrations.AlterModelOptions(
            name='userinfo',
            options={'verbose_name': 'User'},
        ),
        migrations.AlterModelOptions(
            name='userlogin',
            options={'verbose_name': 'Login'},
        ),
    ]
