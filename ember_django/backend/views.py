#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views for django rest framework .

@author: Ioannis Stenos, Nick Vrionis
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from kamaki.clients import ClientError
from authenticate_user import *
from django.views import generic
from get_flavors_quotas import project_list_flavor_quota, \
    retrieve_pending_clusters
from models import *
from serializers import OkeanosTokenSerializer, UserInfoSerializer, \
    ClusterCreationParamsSerializer, ClusterInfoSerializer, \
    ClusterchoicesSerializer, PendingQuotaSerializer, ProjectNameSerializer, \
    MasterIpSerializer, UpdateDatabaseSerializer, TaskSerializer
from django_db_after_login import *
from orka.create_cluster import YarnCluster
from orka.cluster_errors_constants import *
from tasks import createcluster
import exceptions
from celery.result import AsyncResult


logging.addLevelName(REPORT, "REPORT")
logging.addLevelName(SUMMARY, "SUMMARY")
logger = logging.getLogger("report")

logging_level = REPORT
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                   level=logging_level, datefmt='%H:%M:%S')

class MainPageView(generic.TemplateView):
    """Load the template file"""
    template_name = 'index.html'

main_page = MainPageView.as_view()

class JobsView(APIView):
    """
    View to get info for our task.
    """
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    resource_name = 'job'
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        """
        Get method
        """
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            task_id = serializer.data['task_id']
            c_task = AsyncResult(task_id)
            user_token = Token.objects.get(key=request.auth)
            user = UserInfo.objects.get(user_id=user_token.user.user_id)

            if c_task.ready():
                if c_task.successful():
                    return Response({'success': c_task.result})
                return Response({'error': c_task.result["exc_message"]})

            else:
                return Response({'state': c_task.state})
        return Response(serializer.errors)


class DatabaseView(APIView):
    """
    View to handle database updating and retrieving cluster quota
    """
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    resource_name = 'orka'
    serializer_class = UpdateDatabaseSerializer

    def get(self, request, *args, **kwargs):
        """Return pending cluster quota from database."""
        self.serializer_class = ProjectNameSerializer
        serializer = self.serializer_class(data=request.DATA)
        user_token = Token.objects.get(key=request.auth)
        user = UserInfo.objects.get(user_id=user_token.user.user_id)
        if serializer.is_valid():
            quota = retrieve_pending_clusters(user.okeanos_token,
                                              serializer.data['project_name'])
            serializer = PendingQuotaSerializer(quota)
            return Response(serializer.data)

        return Response(serializer.errors)


    def post(self, request, *args, **kwargs):
        """Update database that a cluster is being created"""
        self.serializer_class = ClusterchoicesSerializer
        serializer = self.serializer_class(data=request.DATA)
        user_token = Token.objects.get(key=request.auth)
        user = UserInfo.objects.get(user_id=user_token.user.user_id)
        if serializer.is_valid():
            try:
                db_cluster_create(user, serializer.data)
                return Response({"id": 1, "message": "Requested cluster created in db"})
            except ClientError, e:
                return Response({"id": 1, "message": e.message})
            except Exception, e:
                return Response({"id": 1, "message": e.args[0]})

        return Response(serializer.errors)

    def put(self, request, *args, **kwargs):
        """
        Update database that a cluster is created or is destroyed
        after fatal error.
        """
        serializer = self.serializer_class(data=request.DATA)
        user_token = Token.objects.get(key=request.auth)
        user = UserInfo.objects.get(user_id=user_token.user.user_id)
        if serializer.is_valid():
            try:
                db_cluster_update(user, serializer.data['status'],
                                  serializer.data['cluster_name'],
                                  master_IP=serializer.data['master_IP'],
                                  state=serializer.data['state'])
                return Response({"id": 1, "message": "Requested cluster updated"})
            except ClientError, e:
                return Response({"id": 1, "message": e.message})
            except Exception, e:
                return Response({"id": 1, "message": e.args[0]})
        return Response(serializer.errors)

    def delete(self, request, *args, **kwargs):
        """
        Update database that a cluster is deleted from orka-cli.
        """
        self.serializer_class = MasterIpSerializer
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            user_token = Token.objects.get(key=request.auth)
            user = UserInfo.objects.get(user_id=user_token.user.user_id)
            try:
                db_cluster_destroy(user,
                                   serializer.data['master_IP'])
                return Response({"id": 1, "message": "Requested cluster was deleted from db"})
            except ClientError, e:
                return Response({"id": 1, "message": e.message})
            except Exception, e:
                return Response({"id": 1, "message": e.args[0]})
        # This will be send if user's delete cluster parameters are not de-serialized
        # correctly.
        return Response(serializer.errors)


class StatusView(APIView):
    """
    View to handle requests for retrieving cluster creation parameters
    from ~okeanos and checking user's choices for cluster creation
    coming from ember.
    """
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'cluster'
    serializer_class = ClusterCreationParamsSerializer

    def get(self, request, *args, **kwargs):
        """
        Return a serialized ClusterCreationParams model with information
        retrieved by kamaki calls. User with corresponding status will be
        found by the escience token.
        """
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        retrieved_cluster_info = project_list_flavor_quota(self.user)
        serializer = self.serializer_class(retrieved_cluster_info, many=True)
        return Response(serializer.data)


    def put(self, request, *args, **kwargs):
        """
        Handles ember requests with user's cluster creation parameters.
        Check the parameters with HadoopCluster object from create_cluster
        script.
        """
        self.resource_name = 'clusterchoice'
        self.serializer_class = ClusterchoicesSerializer
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            user_token = Token.objects.get(key=request.auth)
            user = UserInfo.objects.get(user_id=user_token.user.user_id)
            # Dictionary of YarnCluster arguments
            choices = {'name': serializer.data['cluster_name'],
                       'cluster_size': serializer.data['cluster_size'],
                       'cpu_master': serializer.data['cpu_master'],
                       'ram_master': serializer.data['mem_master'],
                       'disk_master': serializer.data['disk_master'],
                       'cpu_slave': serializer.data['cpu_slaves'],
                       'ram_slave': serializer.data['mem_slaves'],
                       'disk_slave': serializer.data['disk_slaves'],
                       'disk_template': serializer.data['disk_template'],
                       'image': serializer.data['os_choice'],
                       'token': user.okeanos_token,
                       'project_name': serializer.data['project_name'],
                       'ssh_key_name': serializer.data['ssh_key_selection']}

            if 'ssh_key_selection' in serializer.data:
                choices.update({'ssh_key_name': serializer.data['ssh_key_selection']})
            c_cluster = createcluster.delay(choices)
            task_id = c_cluster.id

            return Response({"id": 1, "task_id": task_id}, status=status.HTTP_200_OK) #HTTP_202_ACCEPTED
        # This will be send if user's cluster parameters are not de-serialized
        # correctly.
        return Response(serializer.errors)


class SessionView(APIView):
    """View to handle requests from ember for user login and logout"""
    authentication_classes = (EscienceTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrIsCreation, )
    resource_name = 'user'
    serializer_class = OkeanosTokenSerializer
    user = None

    def get(self, request, *args, **kwargs):
        """
        Return a UserInfo object from db.
        User will be found by the escience token.
        """
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        self.serializer_class = UserInfoSerializer(self.user)
        return Response(self.serializer_class.data)

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user with a ~okeanos token.  Return
        appropriate success flag, user id, cluster number
        and escience token or appropriate  error messages in case of
        error.
        """
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token = serializer.data['token']
            if check_user_credentials(token) == AUTHENTICATED:
                self.user = db_after_login(token)
                self.serializer_class = UserInfoSerializer(self.user)
                return Response(self.serializer_class.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Updates user status in database on user logout.
        """
        user_token = Token.objects.get(key=request.auth)
        self.user = UserInfo.objects.get(user_id=user_token.user.user_id)
        db_logout_entry(self.user)
        self.serializer_class = UserInfoSerializer(self.user)
        return Response({"id": "1", "token": "null", "user_id": "null",
                         "cluster": "null"})
