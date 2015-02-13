# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterCreationParams',
            fields=[
                ('id', models.IntegerField(help_text=b'Id needed by ember.js store', serialize=False, verbose_name=b'Id', primary_key=True)),
                ('project_name', models.CharField(help_text=b'Project name from which resources will be requested', max_length=255, null=True, verbose_name=b'Project Name')),
                ('vms_max', models.IntegerField(help_text=b'Maximum Allowed Virtual machines', null=True, verbose_name=b'Max Vms')),
                ('vms_av', djorm_pgarray.fields.IntegerArrayField()),
                ('cpu_max', models.IntegerField(help_text=b'Maximum Allowed Cpus', null=True, verbose_name=b'Max Cpus')),
                ('cpu_av', models.IntegerField(help_text=b'Available Cpus', null=True, verbose_name=b'Available Cpus')),
                ('mem_max', models.IntegerField(help_text=b'Maximum Allowed Ram', null=True, verbose_name=b'Max Ram')),
                ('mem_av', models.IntegerField(help_text=b'Available Ram', null=True, verbose_name=b'Available Ram')),
                ('disk_max', models.IntegerField(help_text=b'Max disk size', null=True, verbose_name=b'Max disk size')),
                ('disk_av', models.IntegerField(help_text=b'Available disk size', null=True, verbose_name=b'Available disk size')),
                ('cpu_choices', djorm_pgarray.fields.IntegerArrayField()),
                ('mem_choices', djorm_pgarray.fields.IntegerArrayField()),
                ('disk_choices', djorm_pgarray.fields.IntegerArrayField()),
                ('disk_template', djorm_pgarray.fields.TextArrayField(dbtype='text')),
                ('os_choices', djorm_pgarray.fields.TextArrayField(dbtype='text')),
                ('pending_status', models.NullBooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Cluster',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClusterInfo',
            fields=[
                ('id', models.AutoField(help_text=b'Auto-increment cluster id', serialize=False, verbose_name=b'Cluster ID', primary_key=True)),
                ('cluster_name', models.CharField(help_text=b'Name of the cluster', max_length=255, verbose_name=b'Cluster Name')),
                ('action_date', models.DateTimeField(help_text=b'Date and time for the creation of this entry', verbose_name=b'Action Date')),
                ('cluster_status', models.CharField(help_text=b'Destroyed/Active/Pending status of the cluster', max_length=1, verbose_name=b'Cluster Status', choices=[(b'0', b'Destroyed'), (b'1', b'Active'), (b'2', b'Pending')])),
                ('cluster_size', models.IntegerField(help_text=b'Total VMs, including master and slave nodes', null=True, verbose_name=b'Cluster Size')),
                ('cpu_master', models.IntegerField(help_text=b'Cpu number of master VM', verbose_name=b'Master Cpu')),
                ('mem_master', models.IntegerField(help_text=b'Ram of master VM', verbose_name=b'Master Ram')),
                ('disk_master', models.IntegerField(help_text=b'Disksize of master VM', verbose_name=b'Master Disksize')),
                ('cpu_slaves', models.IntegerField(help_text=b'Cpu number of Slave VMs', verbose_name=b'Slaves Cpu')),
                ('mem_slaves', models.IntegerField(help_text=b'Ram of slave VMs', verbose_name=b'Slaves Ram')),
                ('disk_slaves', models.IntegerField(help_text=b'Disksize of slave VMs', verbose_name=b'Slaves Disksize')),
                ('disk_template', models.CharField(help_text=b'Disk Template of the cluster', max_length=255, verbose_name=b'Disk Template')),
                ('os_image', models.CharField(help_text=b'Operating system of the cluster', max_length=255, verbose_name=b'OS Image')),
                ('master_IP', models.CharField(help_text=b"IP address of Master's node", max_length=255, null=True, verbose_name=b'Master IP')),
                ('project_name', models.CharField(help_text=b'Project Name where Cluster was created', max_length=255, verbose_name=b'Project Name')),
            ],
            options={
                'verbose_name': 'Cluster',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=40, null=True)),
            ],
            options={
                'verbose_name': 'Token',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user_id', models.AutoField(help_text=b'Auto-increment user id', serialize=False, verbose_name=b'User ID', primary_key=True)),
                ('user_theme', models.CharField(max_length=255, verbose_name=b'User Theme', blank=True)),
                ('uuid', models.CharField(default=b'', help_text=b'Universally unique identifier (for astakos authentication)', unique=True, max_length=255, verbose_name=b'UUID')),
                ('okeanos_token', models.CharField(null=True, max_length=64, blank=True, help_text=b'Okeanos Authentication Token ', unique=True, verbose_name=b'Okeanos Token')),
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
                ('login_status', models.CharField(help_text=b'Login/Logout status of the user', max_length=10, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')])),
                ('media_type', models.IntegerField(help_text=b'Integer value for Browser, OS, other info (lookup tables))', null=True, verbose_name=b'Media Type')),
                ('user_id', models.ForeignKey(help_text=b'User ID', to='backend.UserInfo')),
            ],
            options={
                'verbose_name': 'Login',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.OneToOneField(related_name=b'escience_token', to='backend.UserInfo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clusterinfo',
            name='user_id',
            field=models.ForeignKey(related_name=b'clusters', to='backend.UserInfo', help_text=b'User ID (user ID who owns the cluster)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clustercreationparams',
            name='user_id',
            field=models.ForeignKey(help_text=b'User ID', to='backend.UserInfo'),
            preserve_default=True,
        ),
    ]
