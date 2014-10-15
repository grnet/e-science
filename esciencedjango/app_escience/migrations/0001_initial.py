# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterInfo',
            fields=[
                ('cluster_id', models.AutoField(help_text=b'Auto-increment cluster id', serialize=False, verbose_name=b'Cluster ID', primary_key=True)),
                ('cluster_name', models.CharField(help_text=b'Name of the cluster', max_length=255, verbose_name=b'Cluster Name')),
                ('action_date', models.DateTimeField(help_text=b'Date and time for the creation of this entry', verbose_name=b'Action Date')),
                ('cluster_status', models.CharField(help_text=b'Destroyed/Active status of the cluster', max_length=1, verbose_name=b'Cluster Status', choices=[(b'0', b'Destroyed'), (b'1', b'Active')])),
                ('cluster_size', models.IntegerField(help_text=b'Total VMs, including master and slave nodes', null=True, verbose_name=b'Cluster Size')),
                ('master_flavor_id', models.IntegerField(help_text=b'Master Flavor ID based on KAMAKI API', verbose_name=b'Master Flavor ID')),
                ('slave_flavor_id', models.IntegerField(help_text=b'Slave Flavor ID based on KAMAKI API', verbose_name=b'Slave Flavor ID')),
                ('os_image', models.CharField(help_text=b'Operating system of the cluster', max_length=255, verbose_name=b'OS Image')),
                ('master_IP', models.CharField(help_text=b"IP address of Master's node", max_length=255, verbose_name=b'Master IP')),
            ],
            options={
                'verbose_name': 'Cluster',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user_id', models.AutoField(help_text=b'Auto-increment user id', serialize=False, verbose_name=b'User ID', primary_key=True)),
                ('uuid', models.CharField(default=b'', help_text=b'Universally unique identifier (for astakos authentication)', unique=True, max_length=255, verbose_name=b'UUID')),
            ],
            options={
                'verbose_name': 'User',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('login_id', models.AutoField(help_text=b'Auto-increment login id', serialize=False, verbose_name=b'Login ID', primary_key=True)),
                ('action_date', models.DateTimeField(help_text=b'Date and time for the creation of this entry', verbose_name=b'Action Date')),
                ('login_status', models.CharField(help_text=b'Login/Logout status of the user', max_length=1, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')])),
                ('media_type', models.IntegerField(help_text=b'Integer value for Browser, OS, other info (lookup tables))', null=True, verbose_name=b'Media Type')),
                ('user_id', models.ForeignKey(help_text=b'User ID', to='app_escience.UserInfo')),
            ],
            options={
                'verbose_name': 'Login',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='clusterinfo',
            name='user_id',
            field=models.ForeignKey(help_text=b'User ID (user ID who owns the cluster)', to='app_escience.UserInfo'),
            preserve_default=True,
        ),
    ]
