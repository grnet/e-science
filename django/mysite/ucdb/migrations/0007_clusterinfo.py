# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0006_auto_20140926_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterInfo',
            fields=[
                ('cluster_id', models.AutoField(serialize=False, verbose_name=b'Cluster ID', primary_key=True)),
                ('cluster_name', models.CharField(max_length=255, verbose_name=b'Cluster Name')),
                ('action_date', models.DateTimeField(verbose_name=b'Action Date')),
                ('cluster_status', models.CharField(max_length=255, verbose_name=b'Cluster Status', choices=[(b'0', b'Destroyed'), (b'1', b'Active')])),
                ('cluster_size', models.IntegerField(null=True, verbose_name=b'Cluster Size')),
                ('master_flavor_id', models.IntegerField(verbose_name=b'Master Flavor ID')),
                ('slave_flavor_id', models.IntegerField(verbose_name=b'Slave Flavor ID')),
                ('os_image', models.CharField(max_length=255, verbose_name=b'OS Image')),
                ('master_IP', models.CharField(max_length=255, verbose_name=b'Master IP')),
                ('user_id', models.ForeignKey(to='ucdb.UserInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
