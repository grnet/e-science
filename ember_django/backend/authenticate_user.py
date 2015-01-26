#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script contains classes and functions that
authenticate escience users.

@author: Ioannis Stenos, Nick Vrionis
"""

import logging
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission
from backend.models import Token
from rest_framework import exceptions
from orka.cluster_errors_constants import *

# Constants
AUTHENTICATED = 1
NOT_AUTHENTICATED = 0
# Only method that escience token authentication is not required.
SAFE_METHODS = ['POST']


class EscienceTokenAuthentication(TokenAuthentication):
    """
    Class that inherit the rest_framework default Token authentication class.
    Overrides the Token model used and authenticate_credentials method.
    """

    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)


class IsAuthenticatedOrIsCreation(BasePermission):
    """
    Class for permissions. Only POST method will be allowed without
    Token authentication. Every other method will have to add
    as a request header the escience authentication token.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated()
            )


class IsAuthenticated(BasePermission):
    """
    Class for permissions for database view. Every method will have to add
    as a request header the escience authentication token.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated()
            )


def check_user_credentials(token, auth_url='https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0'):
    """Identity,Account/Astakos. Test ~okeanos authentication credentials"""
    logging.info(' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
        logging.info(' Authentication verified')
        return AUTHENTICATED
    except ClientError:
        logging.error('Authentication failed with url %s and token %s' % (
                      auth_url, token))
        return NOT_AUTHENTICATED
