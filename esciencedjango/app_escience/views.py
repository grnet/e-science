# -*- coding: utf-8 -*-
'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from django.views import generic
from app_escience.models import UserInfo, Token
from app_escience.serializers import OkeanosTokenSerializer, UserInfoSerializer
from app_escience.django_db_after_login import *
from rest_framework.authentication import get_authorization_header


SAFE_METHODS = ['POST']


class EscienceTokenAuthentication(TokenAuthentication):

    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)


class IsAuthenticatedOrIsCreation(BasePermission):
    """
    The request is authenticated as a user, or is a request for login.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated()
            )


class MainPageView(generic.TemplateView):
  template_name =  'index.html'    #'./ES-133/index.html'
  
main_page = MainPageView.as_view()


class SessionView(APIView):
    """
    View to handle requests from ember.
    """
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'user'
    serializer_class = OkeanosTokenSerializer
    user = None

    def get(self, request, *args, **kwargs):
        """
        Return all UserInfo objects in db.
        """

        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        self.serializer_class = UserInfoSerializer(self.user)
        return Response(self.serializer_class.data)

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user with a token.  Return
        appropriate success flag, error messages, user id  and cluster number.
        """
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
