from django.db import models

# Create your models here.

class Tester(models.Model):
  uuid = models.CharField(max_length=300)
  
  def __unicode__(self):
        return self.uuid