import datetime

from django.db import models
from django.conf import settings


# Create your models here.
class UserInfo(models.Model):
    user_id = models.AutoField("User ID", primary_key=True, null=False)
    email = models.EmailField("User's email", null=False)    

    def __str__(self):
        return self.email
    
class UserLogin(models.Model):
    login_id = models.AutoField("Login ID", primary_key=True, null=False)
    user_id = models.ForeignKey(UserInfo, null=False)
    action_date = models.DateTimeField("Action Date", null=False)

    Status=(
      ("0","login"),
      ("1","logout"),    
    )
    
    login_status = models.CharField("Login Status", max_length=255, choices=Status, null=False)
    mediatype = models.IntegerField("Media Type", null=True)

    def __str__(self):
        return self.user_id.email
        
class ClusterInfo(models.Model):
    cluster_id = models.AutoField("Cluster ID", primary_key=True, null=False)
    cluster_name = models.CharField("Cluster Name", max_length=255, null=False)
    action_date = models.DateTimeField("Action Date", null=False)
  
    Status=(
      ("0","Destroyed"),
      ("1","Active"),    
    )
    
    cluster_status = models.CharField("Cluster Status", max_length=255, choices=Status, null=False)
    cluster_size = models.IntegerField("Cluster Size", null=True)
    master_flavor_id = models.IntegerField("Master Flavor ID", null=False)
    slave_flavor_id = models.IntegerField("Slave Flavor ID", null=False)
    os_image = models.CharField("OS Image", max_length=255, null=False)
    master_IP = models.CharField("Master IP", max_length=255, null=False)  
  
    user_id = models.ForeignKey(UserInfo, null=False)
  
    def __str__(self):
        return self.cluster_name
  