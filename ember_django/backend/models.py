#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 e-Science database model
 @author: Vassilis Foteinos, Ioannis Stenos, Nick Vrionis
"""

import logging
import datetime
import binascii
import os
from django.db import models
from djorm_pgarray.fields import IntegerArrayField, TextArrayField
from django.utils import timezone

class UserInfo(models.Model):
    """Definition of a User object model."""
    user_id = models.AutoField("User ID", primary_key=True, null=False,
                               help_text="Auto-increment user id")
    user_theme = models.CharField("User Theme", blank=True, max_length=255)
    uuid = models.CharField("UUID", null=False, blank=False, unique=True,
                            default="", max_length=255,
                            help_text="Universally unique identifier "
                            "(for astakos authentication)")
    okeanos_token = models.CharField('Okeanos Token', max_length=64,
                                     null=True, blank=True, unique=True,
                                     help_text="Okeanos Authentication Token ")

    master_vm_password = models.CharField("Master VM Password", max_length=255,
                               blank=True, help_text="Root password of master VM")


    def is_authenticated(self):
        return True

    class Meta:
        verbose_name = "User"
        app_label = 'backend'

    def __unicode__(self):
        return str(self.user_id)


ACTION_STATUS_CHOICES = (
    ("0", "login"),
    ("1", "logout"),
)


class ClusterCreationParams(models.Model):
    """
    Definition of  ClusterChoices model for retrieving cluster creation
    parameters from okeanos. Imported djorm_pgarray package
    is needed for custom Arrayfields.
    """
    id = models.IntegerField("Id", primary_key=True, null=False,
                                       help_text="Id needed by ember.js store")
    user_id = models.ForeignKey(UserInfo, null=False,
                                   help_text="User ID")
    # Project name
    project_name = models.CharField("Project Name", max_length=255,
                                    null=True, help_text="Project name from"
                                    " which resources will be requested")
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
    #ssh keys
    ssh_keys_names = TextArrayField()  # ArrayField
    pending_status = models.NullBooleanField(default=False)


    class Meta:
        verbose_name = "Cluster"
        app_label = 'backend'


class Token(models.Model):
    """Definition of a e-science Token Authentication model."""
    user = models.OneToOneField(UserInfo, related_name='escience_token')
    key = models.CharField(max_length=40, null=True)
    creation_date = models.DateTimeField('Creation Date')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_token()
            self.creation_date = timezone.now()
        return super(Token, self).save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def update_token(self, *args, **kwargs):
        # checks if an amount of time has passed
        # since the creation of the token
        # and regenerates a new key
        if(timezone.now() >  self.creation_date + datetime.timedelta(seconds=args[0])):
            self.key = self.generate_token()
            self.creation_date = timezone.now()
        return super(Token, self).save()
            
    def __unicode__(self):
        return self.key

    class Meta:
        verbose_name = "Token"
        app_label = 'backend'


class UserLogin(models.Model):
    """Definition of a User Login relationship model."""
    login_id = models.AutoField("Login ID", primary_key=True, help_text="Auto-increment login id")
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
        app_label = 'backend'

    def __unicode__(self):
        return ("%s, %s") % (self.user_id.user_id, self.login_status)


CLUSTER_STATUS_CHOICES = (
    ("0", "Destroyed"),
    ("1", "Active"),
    ("2", "Pending"),
)

class ClusterInfo(models.Model):
    """Definition of a Hadoop Cluster object model."""
    cluster_name = models.CharField("Cluster Name", max_length=255, null=False,
                                    help_text="Name of the cluster")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    cluster_status = models.CharField("Cluster Status", max_length=1,
                                      choices=CLUSTER_STATUS_CHOICES,
                                      null=False, help_text="Destroyed/Active/Pending"
                                      " status of the cluster")
    cluster_size = models.IntegerField("Cluster Size", null=True,
                                       help_text="Total VMs, including master"
                                       " and slave nodes")
    cpu_master = models.IntegerField("Master Cpu", null=False,
                                     help_text="Cpu number of master VM")

    mem_master = models.IntegerField("Master Ram", null=False,
                                     help_text="Ram of master VM")

    disk_master = models.IntegerField("Master Disksize", null=False,
                                      help_text="Disksize of master VM")

    cpu_slaves = models.IntegerField("Slaves Cpu", null=False,
                                     help_text="Cpu number of Slave VMs")

    mem_slaves = models.IntegerField("Slaves Ram", null=False,
                                     help_text="Ram of slave VMs")

    disk_slaves = models.IntegerField("Slaves Disksize", null=False,
                                      help_text="Disksize of slave VMs")

    disk_template = models.CharField("Disk Template", max_length=255, null=False,
                                     help_text="Disk Template of the cluster")

    os_image = models.CharField("OS Image", max_length=255, null=False,
                                help_text="Operating system of the cluster")
    master_IP = models.CharField("Master IP", max_length=255, blank=True,
                                 help_text="IP address of Master's node")
    user_id = models.ForeignKey(UserInfo, null=False, related_name='clusters',
                                help_text="User ID "
                                "(user ID who owns the cluster)")

    project_name = models.CharField("Project Name", max_length=255, null=False,
                                    help_text="Project Name where"
                                    " Cluster was created")

    task_id = models.CharField("Task Id", max_length=255,
                               blank=True, help_text="Celery task id")

    state = models.CharField("Task State", max_length=255,
                               blank=True, help_text="Celery task state")
    
    hadoop_status =  models.CharField("Hadoop Status", max_length=255,
                               blank=True, help_text="Hadoop Status")

    class Meta:
        verbose_name = "Cluster"
        app_label = 'backend'

    def __unicode__(self):
        return ("%d, %s, %d, %s") % (self.id, self.cluster_name, self.cluster_size,
                                 self.cluster_status)
