#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializers file for django rest framework.

@author: Ioannis Stenos, Nick Vrionis
"""

from rest_framework import serializers
from backend.models import UserInfo, ClusterInfo, ClusterCreationParams


class PGArrayField(serializers.WritableField):
    """
    Override from_native and to_native methods for custom serializer
    fields for ClusterCreationParams model.
    """
    def from_native(self, data):
        if isinstance(data, list):
            return data

    def to_native(self, obj):
        return obj


class ClusterCreationParamsSerializer(serializers.ModelSerializer):
    """
    Serializer for ClusterCreationParams model.
    Custom fields are cpu_choices, mem_choices, vms_av, disk_choices,
    disk_template and os_choices. They are custom because their model
    counterparts are arrays.
    """
    cpu_choices = PGArrayField(required=False)
    mem_choices = PGArrayField(required=False)
    vms_av = PGArrayField(required=False)
    disk_choices = PGArrayField(required=False)
    disk_template = PGArrayField(required=False)
    os_choices = PGArrayField(required=False)
    ssh_keys_names = PGArrayField(required=False)
    
    class Meta:
        model = ClusterCreationParams
        fields = ('id', 'user_id', 'project_name', 'vms_max', 'vms_av',
                  'cpu_max', 'cpu_av', 'mem_max', 'mem_av', 'disk_max',
                  'disk_av', 'cpu_choices', 'mem_choices', 'disk_choices',
                  'disk_template', 'os_choices', 'ssh_keys_names')


class OkeanosTokenSerializer(serializers.Serializer):
    """Serializer for okeanos token from ember login."""
    token = serializers.CharField()


class PendingQuotaSerializer(serializers.Serializer):
    """Serializer for pending quota returned from escience database """
    VMs = serializers.IntegerField()
    Cpus = serializers.IntegerField()
    Ram = serializers.IntegerField()
    Disk = serializers.IntegerField()
    Ip = serializers.IntegerField()
    Network = serializers.IntegerField()


class ProjectNameSerializer(serializers.Serializer):
    """ Serializer for project name"""
    project_name = serializers.CharField()


class TaskSerializer(serializers.Serializer):
    """Serializer for the celery task id."""
    task_id = serializers.CharField()


class MasterIpSerializer(serializers.Serializer):
    """ Serializer for master vm ip """
    master_IP = serializers.CharField()


class UpdateDatabaseSerializer(serializers.Serializer):

    status = serializers.CharField()
    cluster_name = serializers.CharField()
    state = serializers.CharField()
    master_IP = serializers.CharField(required=False)


class ClusterchoicesSerializer(serializers.Serializer):
    """
    Serializer for ember request with user's
    choices for cluster creation.
    """
    cluster_name = serializers.CharField()

    cluster_size = serializers.IntegerField()

    cpu_master = serializers.IntegerField()

    mem_master = serializers.IntegerField()

    disk_master = serializers.IntegerField()

    cpu_slaves = serializers.IntegerField()

    mem_slaves = serializers.IntegerField()

    disk_slaves = serializers.IntegerField()

    disk_template = serializers.CharField()

    os_choice = serializers.CharField()

    project_name = serializers.CharField()
    
    ssh_key_selection = serializers.CharField(required=False)

    task_id = serializers.CharField(required=False)


class ClusterInfoSerializer(serializers.ModelSerializer):
    """ Serializer for ember request with user's available clusters."""
    class Meta:
        model = ClusterInfo
        fields = ('id', 'cluster_name', 'cluster_status', 'cluster_size',
                  'cpu_master', 'mem_master', 'disk_master', 'cpu_slaves',
                  'mem_slaves', 'disk_slaves', 'disk_template', 'os_image',
                  'master_IP', 'project_name', 'task_id', 'state', 'master_vm_password')


class UserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for UserInfo object with cluster and escience_token
    added fields.
    """
    cluster = serializers.SerializerMethodField('number_of_clusters')
    escience_token = serializers.RelatedField()
    id = serializers.SerializerMethodField('get_ember_id')
    clusters = ClusterInfoSerializer(many=True)

    class Meta:
        model = UserInfo
        fields = ('id', 'user_id', 'cluster', 'escience_token', 'clusters')

    def number_of_clusters(self, obj):
        """
        Function that calculates the number of clusters of a UserInfo instance.
        """
        clusters = ClusterInfo.objects.all().filter(user_id=obj.user_id). \
            filter(cluster_status=1).count()
        return clusters

    def get_ember_id(self, obj):
        """"Always returns id 1 for ember.js"""
        return 1
