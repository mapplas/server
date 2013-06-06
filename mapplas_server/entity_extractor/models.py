from django.contrib.gis.db import models
from rest_api.models import BigIntegerField

class geonames_all_countries(models.Model):
	identifier = models.IntegerField(primary_key=True)
	name1 = models.TextField()
	name2 = models.TextField()
	name3 = models.TextField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	country = models.CharField(max_length=200)
	
	province = models.CharField(max_length=80, null=True)
	village = models.TextField(null=True)
	
	letter = models.CharField(max_length=10)
	
	undef1 = models.TextField()
	undef2 = models.TextField() #country code - ES
	undef3 = models.TextField()
	undef4 = models.TextField()
	undef5 = models.TextField() #province - SS
	undef6 = models.TextField() #postal-code
	
	number1 = models.CharField(max_length=10)
	number2 = BigIntegerField()
	number3 = models.CharField(max_length=10)
	number4 = models.IntegerField()
	
	data = models.CharField(max_length=30)
	
	objects = models.GeoManager()
	
	# Returns the string representation of the model.
	def __unicode__(self):
		return self.name1 + ' ' + self.country
		
	
		
class EntityTypes(models.Model):
	identifier = models.CharField(primary_key=True, max_length=10)
	name = models.CharField(max_length=50)
	
	objects = models.GeoManager()
	
	# Returns the string representation of the model.
	def __unicode__(self):
		return self.identifier + ' ' + self.name
		
	
		
class Entities(models.Model):
	name1 = models.TextField()
	name2 = models.TextField(null=True)
	
	parent = models.IntegerField(null=True)
	region_type = models.ForeignKey(EntityTypes, on_delete=models.CASCADE, null=True)
	
	lang_code = models.CharField(max_length=10, null=True)
	
	mpoly = models.MultiPolygonField(null=True)
		
	objects = models.GeoManager()
	
	# Returns the string representation of the model.
	def __unicode__(self):
		return self.name1