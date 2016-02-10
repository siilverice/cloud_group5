from __future__ import unicode_literals

from django.db import models

# Create your models here.
class VM(models.Model):
	id = models.AutoField(primary_key=True)
	owner = models.IntegerField(default=0)
	name = models.CharField(max_length=100,unique=True)
	ip = models.CharField(max_length=16,unique=True)
	status = models.IntegerField()
	size = models.FloatField(default=8589.93)
	cost = models.FloatField(default=429.49)
	name_display = models.CharField(max_length=100,default='name')

class Requirements(models.Model):
	vm_name = models.CharField(max_length=100,primary_key=True)
	latency 	= models.FloatField()
	latency_max = models.FloatField()
	percentl 	= models.FloatField()
	iops_min 	= models.FloatField()
	iops  		= models.FloatField()
	percenti  	= models.FloatField()
	cost  		= models.FloatField()
	cost_max  	= models.FloatField()
	percentc  	= models.FloatField()
	app_type  	= models.IntegerField()

class Storage(models.Model):
	vm_name = models.CharField(max_length=100,primary_key=True)
	current_pool = models.CharField(max_length=10)
	appropiate_pool = models.CharField(max_length=10)
	notice = models.IntegerField(default=1)

class Cube(models.Model):
	vm_name = models.CharField(max_length=100,primary_key=True)
	latency_min	= models.FloatField()
	latency 	= models.FloatField()
	latency_max = models.FloatField()
	percentl 	= models.FloatField()
	iops_min 	= models.FloatField()
	iops  		= models.FloatField()
	iops_max	= models.FloatField()
	percenti  	= models.FloatField()
	cost_min	= models.FloatField()
	cost  		= models.FloatField()
	cost_max  	= models.FloatField()
	percentc  	= models.FloatField()
	app_type  	= models.IntegerField()

class State(models.Model):
	vm_name 	= models.CharField(max_length=100,primary_key=True)
	latency 	= models.FloatField()
	iops 		= models.FloatField()
	latency_hdd = models.FloatField()
	iops_hdd 	= models.FloatField()
	latency_ssd = models.FloatField()
	iops_ssd 	= models.FloatField()
		