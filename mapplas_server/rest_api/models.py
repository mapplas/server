from django.contrib.gis.db import models

from django.db.models.fields import IntegerField
from django.conf import settings


class BigIntegerField(IntegerField):
    empty_strings_allowed = False
    def get_internal_type(self):
        return "BigIntegerField"	
    def db_type(self, connection):
        return 'bigint' # Note this won't work with Oracle.



class User(models.Model):
    # If no primary key is set, Django creates it automatically.
    #user_id = models.AutoField(primary_key=True)
    imei = models.CharField(max_length=32)
    tel = models.CharField(max_length=32)
    created = BigIntegerField()
    updated = BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.imei


class UserInstalledApps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    installed_apps = models.TextField()
    lon = models.FloatField()
    lat = models.FloatField()
    created = BigIntegerField()
    updated = BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.user.imei + ': ' + self.installed_apps + ' at lat: ' + self.lat + ' and long: ' + self.lon

'''
class UserLastUsedApps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_used_apps = models.CharField(max_length=256)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    objects = models.GeoManager()

    def __str__(self):
        return self.user.imei + ': ' + self.last_used_apps + ' at lat: ' + self.lat + ' and long: ' + self.lon
'''

class Application(models.Model):
    # app_id_appstore is AppStore Apple ID (ex. 624548749)
    app_id_appstore = models.PositiveIntegerField(primary_key=True)
    
	# app_name is AppStore Bundle ID (ex. Genius Multiplication)
    app_name = models.CharField(max_length=1000)
    
    url_schema = models.CharField(max_length=200, null=True)
    icon_url = models.CharField(max_length=1000, null=True)
    app_description = models.TextField()
    version = models.CharField(max_length=100)
    file_size = BigIntegerField(null=True)
    rec_age = models.CharField(max_length=20, null=True)
    view_url = models.CharField(max_length=1000)
    company_url = models.CharField(max_length=1000, null=True)
    support_url = models.CharField(max_length=1000)
    created = BigIntegerField()
    updated = BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app_name


class UserPinnedApps(models.Model):
    #primary key is autogenerated
    #pin_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    lon = models.FloatField()
    lat = models.FloatField()
    created = BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - " + self.user.imei


class UserBlockedApps(models.Model):
    #primary key is autogenerated
    #block_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    created =BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - " + self.user.imei


class UserSharedApps(models.Model):
    #primary key is autogenerated
    #share_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    lon = models.FloatField()
    lat = models.FloatField()
    via = models.CharField(max_length=32)
    created = BigIntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - " + self.user.imei


class AppDetails(models.Model):
	app_id = models.PositiveIntegerField(primary_key=True)
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
		
		
	def __str__(self):
		return self.app_id + " - (" + self.language_code + ") " + self.title 


class Storefront(models.Model):
    storefront_id = models.IntegerField(primary_key=True)
    country_code = models.CharField('2 Digit ISO', max_length=10)
    name = models.CharField(max_length=200)

    objects = models.GeoManager()

    def __str__(self):
        return self.name


class Geometry(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE)
    polygon = models.MultiPolygonField()
    polygon_developer = models.MultiPolygonField(null=True)

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.storefront.name


class AppPrice(models.Model):
    app_id = models.PositiveIntegerField(primary_key=True)
    storefront_id = models.IntegerField()
    retail_price = models.FloatField()
    currency_code = models.CharField('3 Digit ISO', max_length=20)

    objects = models.GeoManager()
    
    class Meta:
    	unique_together = ('app_id', 'storefront_id')

    def __str__(self):
        return self.app_id + ': ' + self.retail_price


class DeviceType(models.Model):
    device_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    objects = models.GeoManager()

    def __str__(self):
        return  self.name


class AppDeviceType(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.device_type.name


class Developer(models.Model):
    developer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000, null=True)
    url = models.CharField(max_length=1000)

    objects = models.GeoManager()

    def __str__(self):
        return self.name


class DeveloperApp(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.developer.name


class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    parent_id = models.IntegerField(null=True)

    objects = models.GeoManager()

    def __str__(self):
        return self.name


class GenreApp(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    app_id = models.PositiveIntegerField()
    is_primary = models.BooleanField()

    objects = models.GeoManager()
    
    class Meta:
    	unique_together = ('genre_id', 'app_id')

    def __str__(self):
        return self.app_id + ' - ' + self.genre_id


class Ranking(models.Model):
    storefront_id = models.IntegerField()
    app_id = models.PositiveIntegerField(primary_key=True)
    genre_id = models.IntegerField()
    app_rank = models.IntegerField()

    objects = models.GeoManager()
    
    class Meta:
    	unique_together = ('storefront_id', 'app_id', 'genre_id')

    def __str__(self):
        return self.app_id + ' - Storefront: ' + self.storefront_id + ' - Genre: ' + self.genre_id + '. Ranking: ' + self.app_rank


class Review(models.Model):
    review_id = models.IntegerField(primary_key=True)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    language = models.CharField('2 Digit ISO', max_length=2)
    timestamp = models.DateTimeField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=56)
    app_version = models.FloatField()
    device = models.CharField(max_length=56)
    rating = models.FloatField()
    review_text = models.CharField(max_length=1024)

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.language + ' - ' + self.rating