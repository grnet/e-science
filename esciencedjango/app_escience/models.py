"""
 e-Science database model
 @author: Vassilis Foteinos

""" 
import logging 
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator 
from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify 



class UserInfo(models.Model):
    """Definition of a User object model.""" 
    user_id = models.AutoField("User ID", primary_key=True, null=False,
        help_text="Auto-increment user id")
    uuid = models.CharField("UUID", null=False, blank=False, unique=True, default="", max_length=255,
        help_text="Universally unique identifier (for astakos authentication)")

    class Meta:
        verbose_name = "User"


    def __unicode__(self):
        return str(self.user_id)

    
ACTION_STATUS_CHOICES=(
    ("0","login"),
    ("1","logout"),    
)
    
class UserLogin(models.Model):
    """Definition of a User Login relationship model.""" 
    login_id = models.AutoField("Login ID", primary_key=True, null=False,
      help_text="Auto-increment login id")
    user_id = models.ForeignKey(UserInfo, null=False, 
      help_text="User ID")
    action_date = models.DateTimeField("Action Date", null=False,
      help_text="Date and time for the creation of this entry")
    login_status = models.CharField("Login Status", max_length=10,
        choices=ACTION_STATUS_CHOICES, null=False, 
	  help_text="Login/Logout status of the user")
    media_type = models.IntegerField("Media Type", null=True, 
      help_text="Integer value for Browser, OS, other info (lookup tables))")

    class Meta:
        verbose_name = "Login" 


    def __unicode__(self):
        return ("%s, %s") % (self.user_id.user_id, self.login_status)
        

CLUSTER_STATUS_CHOICES=(
    ("0","Destroyed"),
    ("1","Active"),    
)

class ClusterInfo(models.Model):
    """Definition of a Hadoop Cluster object model.""" 
    cluster_id = models.AutoField("Cluster ID", primary_key=True, null=False, 
	help_text="Auto-increment cluster id")
    cluster_name = models.CharField("Cluster Name", max_length=255, null=False, 
	help_text="Name of the cluster")
    action_date = models.DateTimeField("Action Date", null=False, 
	help_text="Date and time for the creation of this entry")
    cluster_status = models.CharField("Cluster Status", max_length=1, 
        choices=CLUSTER_STATUS_CHOICES, null=False, 
	  help_text="Destroyed/Active status of the cluster")
    cluster_size = models.IntegerField("Cluster Size", null=True, 
        help_text="Total VMs, including master and slave nodes")
    master_flavor_id = models.IntegerField("Master Flavor ID", null=False, 
        help_text="Master Flavor ID based on KAMAKI API")
    slave_flavor_id = models.IntegerField("Slave Flavor ID", null=False, 
        help_text="Slave Flavor ID based on KAMAKI API")
    os_image = models.CharField("OS Image", max_length=255, null=False, 
        help_text="Operating system of the cluster")
    master_IP = models.CharField("Master IP", max_length=255, null=False, 
        help_text="IP address of Master's node")  
    user_id = models.ForeignKey(UserInfo, null=False, 
	help_text="User ID (user ID who owns the cluster)")
  
    class Meta:
        verbose_name = "Cluster" 


    def __unicode__(self):
        return ("%s, %d, %s") % (self.cluster_name, self.cluster_size, self.cluster_status)
  