#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Views for django rest framework .

@author: Ioannis Stenos, Nick Vrionis
'''

import os
from os.path import join, dirname, abspath
import sys
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authenticate_user import *
from django.views import generic
from get_flavors_quotas import project_list_flavor_quota
from backend.models import *
from backend.serializers import OkeanosTokenSerializer, UserInfoSerializer, \
    ClusterCreationParamsSerializer, ClusterchoicesSerializer
from django_db_after_login import *
from create_cluster import YarnCluster
from cluster_errors_constants import *


class MainPageView(generic.TemplateView):
    '''Load the template file'''
    template_name = 'index.html'

main_page = MainPageView.as_view()


class StatusView(APIView):
    '''
    View to handle requests for retrieving cluster creation parameters
    from ~okeanos and checking user's choices for cluster creation
    coming from ember.
    '''
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'cluster'
    serializer_class = ClusterCreationParamsSerializer

    def get(self, request, *args, **kwargs):
        '''
        Return a serialized ClusterCreationParams model with information
        retrieved by kamaki calls. User with corresponding status will be
        found by the escience token.
        '''
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        retrieved_cluster_info = project_list_flavor_quota(self.user)
        serializer = self.serializer_class(retrieved_cluster_info, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        '''
        Handles ember requests with user's cluster creation parameters.
        Check the parameters with HadoopCluster object from create_cluster
        script.
        '''
        self.resource_name = 'clusterchoice'
        self.serializer_class = ClusterchoicesSerializer
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            user_token = Token.objects.get(key=request.auth)
            user = UserInfo.objects.get(user_id=user_token.user.user_id)
            # Dictionary of YarnCluster arguments
            choices = {'name': serializer.data['cluster_name'],
                       'clustersize': serializer.data['cluster_size'],
                       'cpu_master': serializer.data['cpu_master'],
                       'ram_master': serializer.data['mem_master'],
                       'disk_master': serializer.data['disk_master'],
                       'cpu_slave': serializer.data['cpu_slaves'],
                       'ram_slave': serializer.data['mem_slaves'],
                       'disk_slave': serializer.data['disk_slaves'],
                       'disk_template': serializer.data['disk_template'],
                       'image': serializer.data['os_choice'],
                       'token': user.okeanos_token,
                       'project_name': serializer.data['project_name']}

            new_yarn_cluster = YarnCluster(choices)
            # Check user's cluster choices and send message if everything ok.
            # Else send appropriate error message.
            cluster_check = new_yarn_cluster.check_all_resources()

            if cluster_check == 0:
                return Response({"id": 1, "message": "Everything is ok with "
                                 "your cluster creation parameters"})
            elif cluster_check == -13:
                return Response({"id": 1, "message": "Selected cluster size "
                                 "exceeded cyclades virtual machines limit"})
            elif cluster_check == -14:
                return Response({"id": 1, "message": "Private Network quota"
                                 " exceeded"})
            elif cluster_check == -30:
                return Response({"id": 1, "message": "Public ip quota "
                                 "exceeded"})
            elif cluster_check == -11:
                return Response({"id": 1, "message": "Cpu selection exceeded"
                                 " cyclades cpu limit"})
            elif cluster_check == -12:
                return Response({"id": 1, "message": "Ram selection exceeded"
                                 " cyclades memory limit"})
            elif cluster_check == -10:
                return Response({"id": 1, "message": "Disk size selection"
                                 " exceeded cyclades disk size limit"})
        # This will be send if user's cluster parameters are not de-serialized
        # correctly.
        return Response(serializer.errors)


class SessionView(APIView):
    '''View to handle requests from ember for user login and logout'''
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'user'
    serializer_class = OkeanosTokenSerializer
    user = None

    def get(self, request, *args, **kwargs):
        '''
        Return a UserInfo object from db.
        User will be found by the escience token.
        '''
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        self.serializer_class = UserInfoSerializer(self.user)
        return Response(self.serializer_class.data)

    def post(self, request, *args, **kwargs):
        '''
        Authenticate a user with a ~okeanos token.  Return
        appropriate success flag, user id, cluster number
        and escience token or appropriate  error messages in case of
        error.
        '''
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token = serializer.data['token']
            if check_user_credentials(token) == AUTHENTICATED:
                self.user = get_user_id(token)
                self.serializer_class = UserInfoSerializer(self.user)
                return Response(self.serializer_class.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        '''
        Updates user status in database on user logout.
        '''
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        db_logout_entry(self.user)
        self.serializer_class = UserInfoSerializer(self.user)
        return Response({"id": "1", "token": "null", "user_id": "null",
                         "cluster": "null"})
