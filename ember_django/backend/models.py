#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
 e-Science database model
 @author: Vassilis Foteinos, Ioannis Stenos, Nick Vrionis
'''

import logging
import datetime
import binascii
import os
from django.db import models
from djorm_pgarray.fields import IntegerArrayField, TextArrayField


class UserInfo(models.Model):
    '''Definition of a User object model.'''
    user_id = models.AutoField("User ID", primary_key=True, null=False,
                               help_text="Auto-increment user id")
    uuid = models.CharField("UUID", null=False, blank=False, unique=True,
                            default="", max_length=255,
                            help_text="Universally unique identifier "
                            "(for astakos authentication)")
    okeanos_token = models.CharField('Okeanos Token', max_length=64,
                                     null=True, blank=True, unique=True,
                                     help_text="Okeanos Authentication Token ")

    def is_authenticated(self):
        return True

    class Meta:
        verbose_name = "User"

    def __unicode__(self):
        return str(self.user_id)


ACTION_STATUS_CHOICES = (
    ("0", "login"),
    ("1", "logout"),
)


class ClusterCreationParams(models.Model):
    '''
    Definition of  ClusterChoices model for retrieving cluster creation
    parameters from okeanos. Imported djorm_pgarray package
    is needed for custom Arrayfields.
    '''
    user_id = models.OneToOneField(UserInfo, null=False,
                                   help_text="User ID")
    # Maximum allowed vms
    vms_max = models.IntegerField("Max Vms", null=True,
                                  help_text="Maximum Allowed Virtual"
                                  " machines")
    # Available vms for user
    vms_av = IntegerArrayField()  # ArrayField
    # Maximum allowed cpus
    cpu_max = models.IntegerField("Max Cpus", null=True,
                                  help_text="Maximum Allowed Cpus")
    # Available cpus
    cpu_av = models.IntegerField("Available Cpus", null=True,
                                 help_text="Available Cpus")
    # Maximum allowed memory
    mem_max = models.IntegerField("Max Ram", null=True,
                                  help_text="Maximum Allowed Ram")
    # Available memory
    mem_av = models.IntegerField("Available Ram", null=True,
                                 help_text="Available Ram")
    # Maximum allowed disk size
    disk_max = models.IntegerField("Max disk size", null=True,
                                   help_text="Max disk size")
    # Available disk size
    disk_av = models.IntegerField("Available disk size", null=True,
                                  help_text="Available disk size")
    # Cpu choices
    cpu_choices = IntegerArrayField()  # ArrayField
    # Memory choices
    mem_choices = IntegerArrayField()  # ArrayField
    # Disk size choices
    disk_choices = IntegerArrayField()  # ArrayField
    # Disk template choices
    disk_template = TextArrayField()  # ArrayField
    # Operating system choices
    os_choices = TextArrayField()  # ArrayField


class Token(models.Model):
    '''Definition of a e-science Token Authentication model.'''
    user = models.OneToOneField(UserInfo, related_name='escience_token')
    key = models.CharField(max_length=40, null=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_token()
        return super(Token, self).save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.key


class UserLogin(models.Model):
    '''Definition of a User Login relationship model.'''
    login_id = models.AutoField("Login ID", primary_key=True, null=False,
                                help_text="Auto-increment login id")
    user_id = models.ForeignKey(UserInfo, null=False,
                                help_text="User ID")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for the "
                                       "creation of this entry")
    login_status = models.CharField("Login Status", max_length=10,
                                    choices=ACTION_STATUS_CHOICES, null=False,
                                    help_text="Login/Logout "
                                    "status of the user")
    media_type = models.IntegerField("Media Type", null=True,
                                     help_text="Integer value for Browser, "
                                     "OS, other info (lookup tables))")

    class Meta:
        verbose_name = "Login"

    def __unicode__(self):
        return ("%s, %s") % (self.user_id.user_id, self.login_status)

CLUSTER_STATUS_CHOICES = (
    ("0", "Destroyed"),
    ("1", "Active"),
)


class ClusterInfo(models.Model):
    '''Definition of a Hadoop Cluster object model.'''
    cluster_id = models.AutoField("Cluster ID", primary_key=True, null=False,
                                  help_text="Auto-increment cluster id")
    cluster_name = models.CharField("Cluster Name", max_length=255, null=False,
                                    help_text="Name of the cluster")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    cluster_status = models.CharField("Cluster Status", max_length=1,
                                      choices=CLUSTER_STATUS_CHOICES,
                                      null=False, help_text="Destroyed/Active"
                                      " status of the cluster")
    cluster_size = models.IntegerField("Cluster Size", null=True,
                                       help_text="Total VMs, including master"
                                       " and slave nodes")
    master_flavor_id = models.IntegerField("Master Flavor ID", null=False,
                                           help_text="Master Flavor ID based"
                                           " on KAMAKI API")
    slave_flavor_id = models.IntegerField("Slave Flavor ID", null=False,
                                          help_text="Slave Flavor ID based"
                                          " on KAMAKI API")
    os_image = models.CharField("OS Image", max_length=255, null=False,
                                help_text="Operating system of the cluster")
    master_IP = models.CharField("Master IP", max_length=255, null=False,
                                 help_text="IP address of Master's node")
    user_id = models.ForeignKey(UserInfo, null=False,
                                help_text="User ID "
                                "(user ID who owns the cluster)")

    class Meta:
        verbose_name = "Cluster"

    def __unicode__(self):
        return ("%s, %d, %s") % (self.cluster_name, self.cluster_size,
                                 self.cluster_status)
