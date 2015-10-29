#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 e-Science database model
 @author: e-science Dev-team
"""

import logging
import datetime
import binascii
import os
from django.db import models
from djorm_pgarray.fields import IntegerArrayField, TextArrayField
from django.utils import timezone
from django.apps import apps as django_apps
django_apps.get_app_config('backend').verbose_name = ' E-Science'

class UserInfo(models.Model):
    """Definition of a User object model."""
    user_id = models.AutoField("User ID", primary_key=True, null=False,
                               help_text="Auto-increment user id")
    user_name = models.CharField("User Name", max_length=255, blank=True,
                                 help_text="Name or email linked to ~okeanos token")    
    user_theme = models.CharField("User Theme", blank=True, max_length=255)
    uuid = models.CharField("UUID", null=False, blank=False, unique=True,
                            default="", max_length=255,
                            help_text="Universally unique identifier "
                            "(for astakos authentication)")
    okeanos_token = models.CharField('Encrypted Okeanos Token', max_length=64,
                                     null=True, blank=True, unique=True,
                                     help_text="Encrypted Okeanos Authentication Token ")
    # master_VM_password is saved temporarily in database and then assigned to blank.
    master_vm_password = models.CharField("Master VM Password", max_length=255,
                               blank=True, help_text="Root password of master VM")
    error_message = models.CharField("Error Message", max_length=255,
                               blank=True, help_text="Error message when status is failed")


    def is_authenticated(self):
        return True

    class Meta:
        verbose_name = "User"

    def __unicode__(self):
        return ('%s : %s') % (self.user_id, self.user_name)


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
    # Maximum allowed ram
    ram_max = models.IntegerField("Max Ram", null=True,
                                  help_text="Maximum Allowed Ram")
    # Available ram
    ram_av = models.IntegerField("Available Ram", null=True,
                                 help_text="Available Ram")
    # Maximum allowed disk size
    disk_max = models.IntegerField("Max disk size", null=True,
                                   help_text="Max disk size")
    # Available disk size
    disk_av = models.IntegerField("Available disk size", null=True,
                                  help_text="Available disk size")
    # network
    net_av = models.IntegerField("Available Networks", null=True,
                                 help_text="Available Networks")
    # floating ips
    floatip_av = models.IntegerField("Available floating IPs", null=True,
                                     help_text="Available floating IPs")
    # Cpu choices
    cpu_choices = IntegerArrayField()  # ArrayField
    # Ram choices
    ram_choices = IntegerArrayField()  # ArrayField
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
        verbose_name = "ClusterParam"


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
        """
        Checks if an amount of time has passed
        since the creation of the token
        and regenerates a new key
        """
        if(timezone.now() >  self.creation_date + datetime.timedelta(seconds=args[0])):
            self.key = self.generate_token()
            self.creation_date = timezone.now()
        return super(Token, self).save()
            
    def __unicode__(self):
        return self.key

    class Meta:
        verbose_name = "Token"


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
        verbose_name = "Login History"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return ("%s : %s : %s") % (self.action_date.strftime('%c'),self.user_id.user_name, ACTION_STATUS_CHOICES[int(self.login_status)][1])


CLUSTER_STATUS_CHOICES = (
    ("0", "Destroyed"),
    ("1", "Active"),
    ("2", "Pending"),
    ("3", "Failed"),
)

HADOOP_STATUS_CHOICES = (
     ("0", "Stopped"),
     ("1", "Started"),
     ("2", "Pending"),
     ("3", "Undefined"),
 )

DSL_STATUS_CHOICES = (
    ("0", "At Rest"),
    ("1", "Replaying"),
)

class VreImageCategory(models.Model):
    """
    Definition of orka VRE image categories.
    """
    id = models.AutoField("VreImageCategory ID", primary_key=True, null=False,
                          help_text="Auto-increment VreImageCategory id")
    category_name = models.CharField("VreImageCategory name", max_length=255, unique=True, null=False,
                                     help_text="VreImageCategory Name")
    class Meta:
        verbose_name_plural = "VRE Image Categories"
    
    def __unicode__(self):
        return ('%s : %s') % (self.id, self.category_name)

class VreImage(models.Model):
    """Definition of orka VRE image information."""
    id = models.AutoField("VreImage ID", primary_key=True, null=False,
                               help_text="Auto-increment VreImage id")
    image_name = models.CharField("Pithos image name", max_length=255, null=False,
                                    help_text="Pithos Image Name")
    image_pithos_uuid = models.CharField("Linked pithos image unique identifier", unique=True, max_length=255, null=False, blank=False,
                                    help_text="Pithos Image UUID")
    image_components = models.CharField("VreImage components metadata", max_length=4080, null=True, blank=True,
                                        help_text="VreImage components metadata as a json dump")
    image_min_reqs = models.CharField("VreImage minimum requirements", max_length=2040, null=True, blank=True,
                                      help_text="VreImage minimum requirements {cpu:xx,ram:xxxx,disk:xx} as a json dump")
    image_faq_links = models.CharField("VreImage F.A.Q. Links", max_length=2040, null=True, blank=True,
                                      help_text="VreImage F.A.Q. Items {label1:url1,label2:url2} as a json dump") 
    image_init_extra = TextArrayField() # extra property fields as field names applying to specific images
    image_access_url = TextArrayField() # array [:port]/path for accessing VRE, base url not included, absence of value assumes base url is access url
    image_category = models.ForeignKey(VreImageCategory, null=False,
                                       help_text="VreImageCategory")
    requires_script = models.BooleanField("Requires shell script", default=True)
    
    class Meta:
        verbose_name = "VRE Image"
    def __unicode__(self):
        return ("%s : %s : %s") % (self.image_category.category_name, self.image_name, self.image_pithos_uuid)

class OrkaImageCategory(models.Model):
    """
    Definition of orka Hadoop image categories.
    """
    id = models.AutoField("OrkaImageCategory ID", primary_key=True, null=False,
                          help_text="Auto-increment OrkaImageCategory id")
    category_name = models.CharField("OrkaImageCategory name", max_length=255, unique=True, null=False,
                                     help_text="OrkaImageCategory Name")
    ansible_cluster_config_tags = models.CharField("OrkaImage ansible cluster config tags", max_length=4080, null=True, blank=True,
                                        help_text="OrkaImage Hadoop cluster configurations ansible tags as a json dump")
    ansible_cluster_action_tags = models.CharField("OrkaImage ansible action tags", max_length=4080, null=True, blank=True,
                                        help_text="OrkaImage Hadoop cluster action (e.g start/stop) ansible tags as a json dump")
    class Meta:
        verbose_name_plural = "Orka Image Categories"
    
    def __unicode__(self):
        return ('%s : %s') % (self.id, self.category_name)

class OrkaImage(models.Model):
    """Definition of orka VM image Components."""
    id = models.AutoField("OrkaImage ID", primary_key=True, null=False,
                               help_text="Auto-increment orkaimage VM id")
    image_name = models.CharField("Pithos image name", max_length=255, null=False,
                                    help_text="Pithos Image Name")
    image_pithos_uuid = models.CharField("Linked pithos image unique identifier", unique=True, max_length=255, null=False, blank=False,
                                    help_text="Pithos Image UUID")
    image_components = models.CharField("OrkaImage components metadata", max_length=4080, null=True, blank=True,
                                        help_text="OrkaImage components metadata as a json dump")
    image_min_reqs = models.CharField("OrkaImage minimum requirements", max_length=2040, null=True, blank=True,
                                      help_text="OrkaImage minimum requirements {cpu:xx,ram:xxxx,disk:xx} as a json dump")
    image_faq_links = models.CharField("OrkaImage F.A.Q. Links", max_length=2040, null=True, blank=True,
                                      help_text="OrkaImage F.A.Q. Items {label1:url1,label2:url2} as a json dump")
    image_init_extra = TextArrayField() # extra property fields as field names applying to specific images
    image_access_url = TextArrayField()
    image_category = models.ForeignKey(OrkaImageCategory, null=False,
                                       help_text="OrkaImageCategory")
    class Meta:
        verbose_name = "Orka Image"
    def __unicode__(self):
        return ("%s : %s") % (self.image_name, self.image_pithos_uuid)

class PublicNewsItem(models.Model):
    """Definition of homepage News Items."""
    id = models.AutoField("Newsitem ID", primary_key=True, null=False,
                               help_text="Auto-increment newsitem id")
    news_date = models.DateTimeField("News Item Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    news_message = models.CharField("News Item Text", max_length=1020, null=False,
                                    help_text="News Item")
    news_category = models.IntegerField("News Item Category", null=True, blank=True,
                                     help_text="Category ID for News Item")
    class Meta:
        verbose_name = "Public News Item"
    def __unicode__(self):
        return ('%s : %s') % (self.news_date.strftime('%c'), self.news_message)

class FaqItemCategory(models.Model):
    """Definition of FAQ Item Categories"""
    id = models.AutoField("FaqItemCategory ID", primary_key=True, null=False,
                          help_text="Auto-increment FaqItemCategory id")
    category_name = models.CharField("FaqItemCategory name", max_length=255, unique=True, null=False,
                                     help_text="FaqItemCategory Name")
    class Meta:
        verbose_name = "Frequently Asked Questions Category"
        verbose_name_plural = "Frequently Asked Questions Categories"
    
    def __unicode__(self):
        return ('%s : %s') % (self.id, self.category_name)
    
class FaqItem(models.Model):
    """Definition of Frequently Asked Questions Items."""
    id = models.AutoField("FaqItem ID", primary_key=True, null=False,
                               help_text="Auto-increment faqitem id")
    faq_date = models.DateTimeField("News Item Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    faq_question = models.CharField("Faq Item Question", max_length=1020, null=False,
                                    help_text="Question")
    faq_answer = models.CharField("Faq Item Answer", max_length=2040, null=False,
                                    help_text="Answer")
    faq_category = models.ForeignKey(FaqItemCategory, null=True, 
                                       help_text="Faq Item Category")
    class Meta:
        verbose_name = "Frequently Asked Question"
        #verbose_name_plural = "Frequently Asked Questions"
    def __unicode__(self):
        return ('Q:%s > A:%s') % (self.faq_question, self.faq_answer)

class OrkaStatistics(models.Model):
    """Definition of Cluster statistics."""
    spawned_clusters = models.IntegerField("Spawned Clusters", null=True,
                                     help_text="Total number of spawned clusters")
    active_clusters = models.IntegerField("Active Clusters", null=True,
                                     help_text="Total number of active clusters")
    spawned_vres = models.IntegerField("Spawned VREs", null=True,
                                       help_text="Total number of spawned Virtual Research Environments")
    active_vres = models.IntegerField("Active VREs", null=True,
                                      help_text="Total number of active Virtual Research Environments")

class ClusterInfo(models.Model):
    """Definition of a Hadoop Cluster object model."""
    cluster_name = models.CharField("Cluster Name", max_length=255, null=False,
                                    help_text="Name of the cluster")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    cluster_status = models.CharField("Cluster Status", max_length=1,
                                      choices=CLUSTER_STATUS_CHOICES,
                                      null=False, help_text="Destroyed/Active/Pending/Failed"
                                      " status of the cluster")
    cluster_size = models.IntegerField("Cluster Size", null=True,
                                       help_text="Total VMs, including master"
                                       " and slave nodes")
    cpu_master = models.IntegerField("Master Cpu", null=False,
                                     help_text="Cpu number of master VM")

    ram_master = models.IntegerField("Master Ram", null=False,
                                     help_text="Ram of master VM")

    disk_master = models.IntegerField("Master Disksize", null=False,
                                      help_text="Disksize of master VM")

    cpu_slaves = models.IntegerField("Slaves Cpu", null=False,
                                     help_text="Cpu number of Slave VMs")

    ram_slaves = models.IntegerField("Slaves Ram", null=False,
                                     help_text="Ram of slave VMs")

    disk_slaves = models.IntegerField("Slaves Disksize", null=False,
                                      help_text="Disksize of slave VMs")

    disk_template = models.CharField("Disk Template", max_length=255, null=False,
                                     help_text="Disk Template of the cluster")

    os_image = models.CharField("OS Image", max_length=255, null=False,
                                help_text="Pithos image used for the creation of the cluster")
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
    
    hadoop_status = models.CharField("Hadoop Status", max_length=1,
                                     choices=HADOOP_STATUS_CHOICES,
                                       blank=False, help_text="Stopped/Started/Pending"
                                       " hadoop status on the cluster")
    
    replication_factor = models.CharField("Replication factor of HDFS", max_length=255, null=False,
                                      help_text="Replication factor of HDFS")
    
    dfs_blocksize = models.CharField("HDFS blocksize in megabytes", max_length=255, null=False,
                                      help_text="HDFS blocksize in megabytes")
    

    class Meta:
        verbose_name = "Cluster"

    def __unicode__(self):
        return ("%d : %s : %s : size(%d) : status(%s) : hadoop(%s)") % (self.id, self.cluster_name, self.os_image, 
                                                                        self.cluster_size,
                                                                        CLUSTER_STATUS_CHOICES[int(self.cluster_status)][1],
                                                                        HADOOP_STATUS_CHOICES[int(self.hadoop_status)][1])
       
class VreServer(models.Model):
    """Definition of a VRE Server object model."""
    server_name = models.CharField("Server Name", max_length=255, null=False,
                                    help_text="Name of the VRE server")
    server_id = models.IntegerField("Server Id", null=False,
                                     help_text="Cyclades Server Id of VRE server")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    server_status = models.CharField("Server Status", max_length=1,
                                      choices=CLUSTER_STATUS_CHOICES,
                                      null=False, help_text="Destroyed/Active/Pending/Failed"
                                      " status of the VRE server")

    cpu = models.IntegerField("Cpu", null=False,
                                     help_text="Cpu number of VRE server")

    ram = models.IntegerField("Ram", null=False,
                                     help_text="Ram of VRE server")

    disk = models.IntegerField("Disksize", null=False,
                                      help_text="Disksize of VRE server")

    disk_template = models.CharField("Disk Template", max_length=255, null=False,
                                     help_text="Disk Template of the VRE server")

    os_image = models.CharField("OS Image", max_length=255, null=False,
                                help_text="Operating system of the VRE server")
    server_IP = models.CharField("VRE Server IP", max_length=255, blank=True,
                                 help_text="IP address of VRE server")
    user_id = models.ForeignKey(UserInfo, null=False, related_name='vreservers',
                                help_text="User ID "
                                "(user ID who owns the VRE server)")

    project_name = models.CharField("Project Name", max_length=255, null=False,
                                    help_text="Project Name where"
                                    " VRE server was created")

    task_id = models.CharField("Task Id", max_length=255,
                               blank=True, help_text="Celery task id")

    state = models.CharField("Task State", max_length=255,
                               blank=True, help_text="Celery task state")
    
    class Meta:
        verbose_name = "VRE Server"

    def __unicode__(self):
        return ("%d : %s : %s : %s") % (self.id, self.server_name, self.os_image, CLUSTER_STATUS_CHOICES[int(self.server_status)][1])
    
class Dsl(models.Model):
    """Definition of a User Reproducible Experiment model."""
    dsl_name = models.CharField("DSL Name", max_length=255, null=False,
                                    help_text="Name of the DSL")
    pithos_path = models.CharField("Pithos path", max_length=255, null=False,
                                     help_text="Pithos path of DSL file")
    action_date = models.DateTimeField("Action Date", null=False,
                                       help_text="Date and time for"
                                       " the creation of this entry")
    dsl_status = models.CharField("Experiment Status", max_length=1, default="0",
                                      choices=DSL_STATUS_CHOICES,
                                      null=False, help_text="At Rest/Replaying"
                                      " status of the Experiment")
    cluster_id = models.IntegerField("Linked Cluster Id", null=True, blank=True,
                                     help_text="Cluster Id from which the DSL metadata was extracted.")

    user = models.ForeignKey(UserInfo, null=False, related_name='dsls',
                                help_text="User ID "
                                "(user ID who owns the DSL File)")

    task_id = models.CharField("Task Id", max_length=255,
                               blank=True, help_text="Celery task id")

    state = models.CharField("Task State", max_length=255,
                               blank=True, help_text="Celery task state")
    
    dsl_data = models.TextField("DSL data", max_length=4090, null=True,
                                     blank=True, help_text="DSL data in yaml format.")
    
    class Meta:
        verbose_name = "Experiment"

    def __unicode__(self):
        return ("%s : cluster_id(%s) : %s") % (self.dsl_name, (self.cluster_id or ''), DSL_STATUS_CHOICES[int(self.dsl_status)][1])
    
class Setting(models.Model):
    """
    Definition of an instance setting kept in backend DB to be managed through Django admin.
    Roughly follows the .ini spec: section > property, where property is a key=value pair. 
    property names are unique per section. Validation is done case insensitive but case is preserved. 
    We also keep an optional comment column.
    """
    id = models.AutoField("Setting ID", primary_key=True, null=False, 
                          help_text="Auto-increment setting id")
    section = models.CharField("Section", max_length=255, null=False,
                                     help_text="Settings section label")
    property_name = models.CharField("Property Name", max_length=255, null=False, 
                                     help_text="Settings property name, must be unique for section")
    property_value = models.CharField("Property Value", max_length=2040, null=False, 
                                     help_text="Settings property value")
    comment = models.CharField("Comments", max_length=1020, null=True, blank=True,
                               help_text="Setting comment")
    
    class Meta:
        verbose_name = "Application Setting"
        unique_together = ("section","property_name")
        
    def __unicode__(self):
        return ("%s : %s : %s") % (self.section, self.property_name, self.property_value)
