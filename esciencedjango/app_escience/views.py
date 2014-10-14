# -*- coding: utf-8 -*-
'''
This script creates a virtual cluster on ~okeanos and installs Hadoop
using Ansible.

@author: Ioannis Stenos, Nick Vrionis
'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views import generic
from app_escience.models import UserInfo
from app_escience.serializers import TokenSerializer, UserInfoSerializer
from app_escience.django_db_after_login import *

class MainPageView(generic.TemplateView):
  template_name = 'index.html'
  
main_page = MainPageView.as_view()

class SessionView(APIView):
    """
    View to handle requests from ember.
    """
    resource_name = 'user'
    serializer_class = TokenSerializer
    user = None
    serializer_class_2 = UserInfoSerializer

    def get(self, request, *args, **kwargs):
        """
        Return all UserInfo objects in db.
        """
        queryset = UserInfo.objects.all()
        serializer = self.serializer_class_2(queryset, many=True)
        return Response(serializer.data)

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
                serializer = UserInfoSerializer(self.user)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
