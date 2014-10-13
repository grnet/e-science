# -*- coding: utf-8 -*-
'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_escience.models import UserInfo
from app_escience.serializers import TokenSerializer, UserInfoSerializer
from app_escience.django_db_after_login import *



class SessionView(APIView):
    """
    View to retrieve the current session if one exists, create a new
    session using a valid username and password, or destroy the session.
    """
    serializer_class = TokenSerializer
    user = None
    cluster = 0
    serializer_class_2 = UserInfoSerializer(user)

    def get(self, request, *args, **kwargs):
        """
        Return the user id associated with this session if one exists.
        """
        return Response(self.serializer_class_2.data)

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user with a token.  Return
        appropriate success flag, error messages, and user id.
        """
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token = serializer.data['token']
            if check_credentials(token) == AUTHENTICATED:
                self.user = get_user_id(token)
                self.serializer_class_2 = UserInfoSerializer(self.user)
                return Response(self.serializer_class_2.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
