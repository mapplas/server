from django.contrib.gis.db import models

from django.db.models.fields import IntegerField
from django.conf import settings


class BigIntegerField(IntegerField):
    empty_strings_allowed = False
    def get_internal_type(self):
        return "BigIntegerField"	
    def db_type(self):
        return 'bigint' # Note this won't work with Oracle.




class User(models.Model):
    # If no primary key is set, Django creates it automatically.
    #user_id = models.AutoField(primary_key=True)
    imei = models.CharField(max_length=32)
    tel = models.CharField(max_length=32)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    objects = models.GeoManager()

    def __str__(self):
        return self.imei


class UserInstalledApps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    installed_apps = models.TextField()
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

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
    icon_url = models.CharField(max_length=1000)
    app_description = models.TextField()
    version = models.CharField(max_length=100)
    file_size = BigIntegerField()
    rec_age = models.CharField(max_length=20, null=True)
    view_url = models.CharField(max_length=1000)
    company_url = models.CharField(max_length=1000, null=True)
    support_url = models.CharField(max_length=1000)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

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
    created = models.DateTimeField('Creation date')

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - " + self.user.imei


class UserBlockedApps(models.Model):
    #primary key is autogenerated
    #block_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    created = models.DateTimeField('Creation date')

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
    created = models.DateTimeField('Creation date')

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - " + self.user.imei


class AppDetails(models.Model):
    #primary key is autogenerated
    #app_id =
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    language_code = models.CharField('2 Digit ISO', max_length=20)
    title = models.CharField(max_length=1000)
    description = models.TextField()
    screenshots = models.TextField()
    company_url = models.CharField(max_length=1000, null=True)
    support_url = models.CharField(max_length=1000)
    release_notes = models.TextField(null=True)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + " - (" + self.language_code + ") " + self.title 


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
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE)
    retail_price = models.FloatField()
    currency_code = models.CharField('3 Digit ISO', max_length=20)

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ': ' + self.retail_price


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
    name = models.CharField(max_length=1000)
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
    parent_id = models.IntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.name


class GenreApp(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    is_primary = models.BooleanField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.genre.name


class Ranking(models.Model):
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    app_rank = models.IntegerField()

    objects = models.GeoManager()

    def __str__(self):
        return self.app.app_name + ' - ' + self.storefront.country_code + ' - ' + self.genre.name + '. Ranking: ' + self.app_rank


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