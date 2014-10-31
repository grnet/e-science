#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Serializers file for django rest framework.

@author: Ioannis Stenos, Nick Vrionis
'''

from rest_framework import serializers
from backend.models import UserInfo
from backend.models import ClusterInfo


class OkeanosTokenSerializer(serializers.Serializer):
    '''Serializer for okeanos token from ember login.'''
    token = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    '''
    Serializer for UserInfo object with cluster and escience_token
    added fields.
    '''
    cluster = serializers.SerializerMethodField('number_of_clusters')
    escience_token = serializers.RelatedField()

    class Meta:
        model = UserInfo
        fields = ('user_id', 'cluster', 'escience_token')

    def number_of_clusters(self, obj):
        '''
        Function that calculates the number of clusters of a UserInfoinstance.
        '''
        clusters = ClusterInfo.objects.all().filter(user_id=obj.user_id). \
            filter(cluster_status=1).count()
        return clusters

