#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Views for django rest framework .

@author: Ioannis Stenos, Nick Vrionis
'''

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authenticate_user import EscienceTokenAuthentication, IsAuthenticatedOrIsCreation
from django.views import generic
from backend.get_flavors_quotas import retrieve_ClusterCreationParams
from backend.models import UserInfo
from backend.serializers import OkeanosTokenSerializer, UserInfoSerializer, ClusterCreationParamsSerializer
from backend.django_db_after_login import *


class MainPageView(generic.TemplateView):
    '''Load the template file'''
    template_name = 'index.html'

main_page = MainPageView.as_view()


class StatusView(APIView):
    '''
    View to handle requests for retrieving cluster creation parameters
    from ~okeanos.
    '''
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'createcluster'
    serializer_class = ClusterCreationParamsSerializer

    def get(self, request, *args, **kwargs):
        '''
        Return a serialized ClusterCreationParams model with information
        retrieved by kamaki calls. User with corresponding status will be
        found by the escience token.
        '''
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        retrieved_cluster_info = retrieve_ClusterCreationParams(self.user)
        serializer = self.serializer_class(retrieved_cluster_info)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        '''
        Not used right now, just a placeholder. Will be needed later
        for passing the ClusterCreationParams information from client
        to okeanos.
        '''
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            return Response({"id": "1"})
        return Response({"id": "1"})


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
            if check_credentials(token) == AUTHENTICATED:
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
