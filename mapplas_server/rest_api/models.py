from django.contrib.gis.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    imei = models.CharField(max_length=45)
    tel = models.CharField(max_length=45)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    def __unicode__(self):
        return self.imei


class UserInstalledApps(models.Model):
    user = models.ForeignKey(User)
    installed_apps = models.CharField(max_length=512)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')


class UserLastUsedApps(models.Model):
    user = models.ForeignKey(User)
    last_used_apps = models.CharField(max_length=256)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')


class Application(models.Model):
    app_id = models.CharField(primary_key=True, max_length=128)
    app_name = models.CharField(max_length=64)
    icon_url = models.CharField(max_length=128)
    app_title = models.CharField(max_length=128)
    app_description = models.CharField(max_length=1024)
    version = models.FloatField()
    file_size = models.FloatField()
    downloads = models.FloatField()
    view_url = models.FloatField(max_length=128)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    def __unicode__(self):
        return self.app_name


class AppDetails(models.Model):
    app = models.ForeignKey(Application)
    language_code = models.CharField('2 Digit ISO', max_length=2)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    screenshots = models.CharField(max_length=1024)
    video = models.CharField(max_length=128)
    company_url = models.CharField(max_length=128)
    support_url = models.CharField(max_length=128)
    release_notes = models.CharField(max_length=256)
    created = models.DateTimeField('Creation date')
    updated = models.DateTimeField('Update date')

    def __unicode__(self):
        return self.title


class Storefront(models.Model):
    storefront_id = models.IntegerField(primary_key=True)
    country_code = models.CharField('2 Digit ISO', max_length=2)
    name = models.CharField(max_length=64)


class Geometry(models.Model):
    app = models.ForeignKey(Application)
    storefront = models.ForeignKey(Storefront)
    polygon = models.MultiPolygonField()
    polygon_developer = models.MultiPolygonField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.polygon.description


class UserPinnedApps(models.Model):
    pin_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    app = models.ForeignKey(Application)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')


class UserBlockedApps(models.Model):
    block_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    app = models.ForeignKey(Application)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')


class UserSharedApps(models.Model):
    share_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    app = models.ForeignKey(Application)
    lon = models.FloatField()
    lat = models.FloatField()
    created = models.DateTimeField('Creation date')


class AppPrice(models.Model):
    app = models.ForeignKey(Application)
    storefront = models.ForeignKey(Storefront)
    retail_price = models.FloatField()
    currency_code = models.CharField('3 Digit ISO', max_length=3)


class DeviceType(models.Model):
    device_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return  self.name


class AppDeviceType(models.Model):
    app = models.ForeignKey(Application)
    device_type = models.ForeignKey(DeviceType)


class Developer(models.Model):
    developer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    email = models.CharField(max_length=128)


class DeveloperApp(models.Model):
    app = models.ForeignKey(Application)
    developer = models.ForeignKey(Developer)


class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)


class GenreApp(models.Model):
    genre = models.ForeignKey(Genre)
    app = models.ForeignKey(Application)
    is_primary = models.BooleanField()


class Ranking(models.Model):
    storefront = models.ForeignKey(Storefront)
    app = models.ForeignKey(Application)
    genre = models.ForeignKey(Genre)
    app_rank = models.IntegerField()
    date = models.DateTimeField()


class Review(models.Model):
    review_id = models.IntegerField(primary_key=True)
    app = models.ForeignKey(Application)
    language = models.CharField('2 Digit ISO', max_length=2)
    timestamp = models.DateTimeField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=56)
    app_version = models.FloatField()
    device = models.CharField(max_length=56)
    rating = models.FloatField()
    review_text = models.CharField(max_length=1024)