# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0007_clusterinfo'),
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
        migrations.RenameField(
            model_name='userlogin',
            old_name='mediatype',
            new_name='media_type',
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_status',
            field=models.CharField(max_length=1, verbose_name=b'Cluster Status', choices=[(b'0', b'Destroyed'), (b'1', b'Active')]),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(help_text=b'User email (username for astakos authentication)', max_length=75, verbose_name=b'User email'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='user_id',
            field=models.AutoField(help_text=b'Auto-increment user id (primary key)', serialize=False, verbose_name=b'User ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='login_status',
            field=models.CharField(max_length=1, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')]),
        ),
    ]
