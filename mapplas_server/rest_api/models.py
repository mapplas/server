# -*- encoding: utf-8 -*-

from django.contrib.gis.db import models

from django.db.models.fields import IntegerField
from django.conf import settings

from entity_extractor.models import Entities


class BigIntegerField(IntegerField):
    empty_strings_allowed = False
    def get_internal_type(self):
        return "BigIntegerField"	
    def db_type(self, connection):
        return 'bigint' # Note this won't work with Oracle.


class Developer(models.Model):
    developer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000, null=True)
    url = models.CharField(max_length=1000)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    parent_id = models.IntegerField(null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class Application(models.Model):
    # app_id_appstore is AppStore Apple ID (ex. 624548749)
    app_id_appstore = models.PositiveIntegerField(primary_key=True)
    
	# app_name is AppStore Bundle ID (ex. Genius Multiplication)
    app_name = models.CharField(max_length=1000)
    
    url_schema = models.CharField(max_length=200, null=True)
    icon_url = models.CharField(max_length=1000, null=True)
    icon_url_retina = models.CharField(max_length=1000, null=True)
    app_description = models.TextField()
    version = models.CharField(max_length=100)
    file_size = BigIntegerField(null=True)
    rec_age = models.CharField(max_length=20, null=True)
    view_url = models.CharField(max_length=1000)
    company_url = models.CharField(max_length=1000, null=True)
    support_url = models.CharField(max_length=1000)
    
    is_web = models.IntegerField(null=True, blank=True)
    
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
        
    created = BigIntegerField()
    updated = BigIntegerField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.app_name


class AppDetails(models.Model):
	app_id = models.PositiveIntegerField()
	language_code = models.CharField('2 Digit ISO', max_length=20)
	title = models.CharField(max_length=1000)
	description = models.TextField()
	screenshot1 = models.CharField(max_length=1000, null=True)
	screenshot2 = models.CharField(max_length=1000, null=True)
	screenshot3 = models.CharField(max_length=1000, null=True)
	screenshot4 = models.CharField(max_length=1000, null=True)
	company_url = models.CharField(max_length=1000, null=True)
	support_url = models.CharField(max_length=1000, null=True)
	release_notes = models.TextField(null=True)
	created = BigIntegerField()
	updated = BigIntegerField()
	
	objects = models.GeoManager()
	
	class Meta:
		unique_together = ('app_id', 'language_code')
		
		
	def __unicode__(self):
		return " - (" + self.language_code + ") " + self.title 


class Storefront(models.Model):
    storefront_id = models.IntegerField(primary_key=True)
    country_code = models.CharField('2 Digit ISO', max_length=10)
    name = models.CharField(max_length=200)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class Geometry(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entities, on_delete=models.CASCADE)
    origin = models.CharField(max_length=10, null=True)
    ranking = models.FloatField(null=True)
    
    objects = models.GeoManager()

    def __unicode__(self):
        return self.app.app_name + ' - ' + self.storefront.name


class AppPrice(models.Model):
    app_id = models.PositiveIntegerField()
    storefront_id = models.IntegerField()
    retail_price = models.FloatField()
    currency_code = models.CharField('3 Digit ISO', max_length=20)

    objects = models.GeoManager()
    
    class Meta:
    	unique_together = ('app_id', 'storefront_id')

    def __unicode__(self):
        return self.app_id + ': ' + self.retail_price


class DeviceType(models.Model):
    device_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    objects = models.GeoManager()

    def __unicode__(self):
        return  self.name


class AppDeviceType(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.app.app_name + ' - ' + self.device_type.name


class Ranking(models.Model):
    storefront_id = models.IntegerField()
    app_id = models.PositiveIntegerField()
    genre_id = models.IntegerField()
    app_rank = models.IntegerField()

    objects = models.GeoManager()
    
    class Meta:
    	unique_together = ('storefront_id', 'app_id', 'genre_id')

    def __unicode__(self):
        return self.app_id + ' - Storefront: ' + self.storefront_id + ' - Genre: ' + self.genre_id + '. Ranking: ' + self.app_rank


# class Review(models.Model):
#     review_id = models.IntegerField(primary_key=True)
#     app = models.ForeignKey(Application, on_delete=models.CASCADE)
#     language = models.CharField('2 Digit ISO', max_length=2)
#     timestamp = models.DateTimeField()
#     user_id = models.IntegerField()
#     user_name = models.CharField(max_length=56)
#     app_version = models.FloatField()
#     device = models.CharField(max_length=56)
#     rating = models.FloatField()
#     review_text = models.CharField(max_length=1024)
# 
#     objects = models.GeoManager()
# 
#     def __str__(self):
#         return self.app.app_name + ' - ' + self.language + ' - ' + self.rating
# 
#  
# class MapplasCathegories(models.Model):
# 	id = models.IntegerField(primary_key=True)
# 	name = models.CharField(max_length=200)
# 	
# 	objects = models.GeoManager()
# 	
# 	def __str__(self):
# 		return self.name
# 		
# 		
# class CathegoryRelationMatrix(models.Model):
# 	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
# 	mapplas_cathegories = models.ForeignKey(MapplasCathegories, on_delete=models.CASCADE)
# 	
# 	objects = models.GeoManager()
# 	
# 	def __str__(self):
# 		return self.genre.name + ' - ' + self.mapplas_cathegories.name
# 		
# 	
# class ChainCathegory(models.Model):
# 	entity = models.ForeignKey(Entities, on_delete=models.CASCADE)
# 	mapplas_cathegories = models.ForeignKey(MapplasCathegories, on_delete=models.CASCADE)
# 	
# 	objects = models.GeoManager()
# 	
# 	def __str__(self):
# 		return self.entity.name + ' - ' + self.mapplas_cathegories.name
# 		
# 
# class UserAppStoreInteraction(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	app = models.ForeignKey(Application, on_delete=models.CASCADE)
# 	lon = models.FloatField()
# 	lat = models.FloatField()
# 	created = BigIntegerField()
# 	
# 	objects = models.GeoManager()
# 	
# 	def __str__(self):
# 		return self.app.app_name + " - " + self.user.user_id
		
class VipDeveloper(models.Model):
	developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
	
	objects = models.GeoManager()

	def __unicode__(self):
		return self.app.developer.name