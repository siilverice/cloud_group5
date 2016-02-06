from __future__ import unicode_literals

from django.db import models

# Create your models here.
class vm(models.Model):
	id = models.AutoField(primary_key=True)
	owner = models.IntegerField()
	name = models.CharField(max_length=100,unique=True)
	ip = models.CharField(max_length=16,unique=True)
	status = models.IntegerField()
	size = models.FloatField(default=8589.93)
	cost = models.FloatField(default=429.49)

class requirements(models.Model):
	vm_name = models.CharField(max_length=100,primary_key=True)
	latency 	= models.IntegerField()
	latency_max = models.IntegerField()
	percentl 	= models.IntegerField()
	iops_min 	= models.IntegerField()
	iops  		= models.IntegerField()
	percenti  	= models.IntegerField()
	cost  		= models.IntegerField()
	cost_max  	= models.IntegerField()
	percentc  	= models.IntegerField()
	app_type  	= models.IntegerField()

class storage(models.Model):
	vm_name = models.CharField(max_length=100,primary_key=True)
	current_pool = models.CharField(max_length=10)
	appropiate_pool = models.CharField(max_length=10)
