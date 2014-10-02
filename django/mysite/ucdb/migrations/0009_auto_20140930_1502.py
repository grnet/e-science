# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ucdb', '0008_auto_20140930_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clusterinfo',
            name='action_date',
            field=models.DateTimeField(help_text=b'Date and time for the creation of this entry', verbose_name=b'Action Date'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_id',
            field=models.AutoField(help_text=b'Auto-increment cluster id', serialize=False, verbose_name=b'Cluster ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_name',
            field=models.CharField(help_text=b'Name of the cluster', max_length=255, verbose_name=b'Cluster Name'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_size',
            field=models.IntegerField(help_text=b'Total VMs, including master and slave nodes', null=True, verbose_name=b'Cluster Size'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_status',
            field=models.CharField(help_text=b'Destroyed/Active status of the cluster', max_length=1, verbose_name=b'Cluster Status', choices=[(b'0', b'Destroyed'), (b'1', b'Active')]),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='master_IP',
            field=models.CharField(help_text=b"IP address of Master's node", max_length=255, verbose_name=b'Master IP'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='master_flavor_id',
            field=models.IntegerField(help_text=b'Master Flavor ID based on KAMAKI API', verbose_name=b'Master Flavor ID'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='os_image',
            field=models.CharField(help_text=b'Operating system of the cluster', max_length=255, verbose_name=b'OS Image'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='slave_flavor_id',
            field=models.IntegerField(help_text=b'Slave Flavor ID based on KAMAKI API', verbose_name=b'Slave Flavor ID'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='user_id',
            field=models.ForeignKey(help_text=b'User ID (user ID who owns the cluster)', to='ucdb.UserInfo'),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='action_date',
            field=models.DateTimeField(help_text=b'Date and time for the creation of this entry', verbose_name=b'Action Date'),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='login_id',
            field=models.AutoField(help_text=b'Auto-increment login id', serialize=False, verbose_name=b'Login ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='login_status',
            field=models.CharField(help_text=b'Login/Logout status of the user', max_length=1, verbose_name=b'Login Status', choices=[(b'0', b'login'), (b'1', b'logout')]),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='media_type',
            field=models.IntegerField(help_text=b'Integer value for Browser, OS, other info (lookup tables))', null=True, verbose_name=b'Media Type'),
        ),
        migrations.AlterField(
            model_name='userlogin',
            name='user_id',
            field=models.ForeignKey(help_text=b'User ID', to='ucdb.UserInfo'),
        ),
    ]
