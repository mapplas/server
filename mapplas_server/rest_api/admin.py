# -*- encoding: utf-8 -*-

from django.contrib.gis import admin

from rest_api.models import Application, AppDetails, Geometry, Developer, DeveloperApp, Storefront, AppPrice
from entity_extractor.models import Entities


# Application
class ApplicationAdmin(admin.OSMGeoAdmin):
	fields = ['app_id_appstore', 'app_name', 'url_schema', 'icon_url', 'icon_url_retina', 'app_description', 'version', 'file_size', 'rec_age', 'view_url', 'company_url', 'support_url', 'created', 'updated']
	search_fields = ['app_id_appstore']

admin.site.register(Application, ApplicationAdmin)


# AppDetails
class AppDetailsAdmin(admin.OSMGeoAdmin):
	fields = ['app_id', 'language_code', 'title', 'description', 'screenshot1', 'screenshot2', 'screenshot3', 'screenshot4', 'company_url', 'support_url', 'release_notes', 'created', 'updated']

admin.site.register(AppDetails, AppDetailsAdmin)


# Geometry
class GeometryAdmin(admin.OSMGeoAdmin):
	fields = ['app', 'entity', 'storefront', 'origin', 'ranking']

	raw_id_fields = ['app', 'entity']
	search_fields = ['app__app_id_appstore', 'entity__name1']
	
admin.site.register(Geometry, GeometryAdmin)


# Storefront
class StorefrontAdmin(admin.OSMGeoAdmin):
	fields = ['storefront_id', 'country_code', 'name']

admin.site.register(Storefront, StorefrontAdmin)


# AppPrice
class AppPriceAdmin(admin.OSMGeoAdmin):
	fields = ['app_id', 'storefront_id', 'retail_price', 'currency_code']
	search_fields = ['app_id']
	
admin.site.register(AppPrice, AppPriceAdmin)

 
# Entities
class EntityAdmin(admin.OSMGeoAdmin):
	fields = ['name1', 'name2', 'region_type', 'lang_code', 'lang_code2', 'storefront', 'mpoly']
	search_fields = ['name1']

admin.site.register(Entities, EntityAdmin)


# Developer
class DeveloperAdmin(admin.OSMGeoAdmin):
	fields = ['developer_id', 'name', 'url']
	
admin.site.register(Developer, DeveloperAdmin)


# DeveloperApp
class DeveloperAppAdmin(admin.OSMGeoAdmin):
	fields = ['app_id', 'developer_id']
	
admin.site.register(DeveloperApp, DeveloperAppAdmin)