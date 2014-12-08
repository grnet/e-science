#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Serializers file for django rest framework.

@author: Ioannis Stenos, Nick Vrionis
'''

from rest_framework import serializers
from backend.models import UserInfo, ClusterInfo, ClusterCreationParams
import random


class PGArrayField(serializers.WritableField):
    '''
    Override from_native and to_native methods for custom serializer
    fields for ClusterCreationParams model.
    '''
    def from_native(self, data):
        if isinstance(data, list):
            return data

    def to_native(self, obj):
        return obj


class ClusterCreationParamsSerializer(serializers.ModelSerializer):
    '''
    Serializer for ClusterCreationParams model.
    Custom fields are cpu_choices, mem_choices, vms_av, disk_choices,
    disk_template and os_choices. They are custom because their model
    counterparts are arrays.
    '''
    cpu_choices = PGArrayField(required=False)
    mem_choices = PGArrayField(required=False)
    vms_av = PGArrayField(required=False)
    disk_choices = PGArrayField(required=False)
    disk_template = PGArrayField(required=False)
    os_choices = PGArrayField(required=False)

    class Meta:
        model = ClusterCreationParams
        fields = ('id', 'user_id', 'project_name', 'vms_max', 'vms_av',
                  'cpu_max', 'cpu_av', 'mem_max', 'mem_av', 'disk_max',
                  'disk_av', 'cpu_choices', 'mem_choices', 'disk_choices',
                  'disk_template', 'os_choices')


class OkeanosTokenSerializer(serializers.Serializer):
    '''Serializer for okeanos token from ember login.'''
    token = serializers.CharField()


class ClusterchoicesSerializer(serializers.Serializer):
    '''
    Serializer for ember request with user's
    choices for cluster creation.
    '''
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


class UserInfoSerializer(serializers.ModelSerializer):
    '''
    Serializer for UserInfo object with cluster and escience_token
    added fields.
    '''
    cluster = serializers.SerializerMethodField('number_of_clusters')
    escience_token = serializers.RelatedField()
    id = serializers.SerializerMethodField('get_ember_id')

    class Meta:
        model = UserInfo
        fields = ('id', 'user_id', 'cluster', 'escience_token')

    def number_of_clusters(self, obj):
        '''
        Function that calculates the number of clusters of a UserInfo instance.
        '''
        clusters = ClusterInfo.objects.all().filter(user_id=obj.user_id). \
            filter(cluster_status=1).count()
        return clusters

    def get_ember_id(self, obj):
        '''Always returns id 1 for ember.js'''
        return 1
