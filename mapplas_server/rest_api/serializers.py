from django.forms import widgets

from rest_framework import serializers
from rest_api.models import User, Application, UserPinnedApps, UserBlockedApps, UserSharedApps, AppDetails, AppDeviceType, DeviceType, AppPrice

class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('id', 'imei', 'tel', 'created', 'updated')
		

class ApplicationSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Application
		fields = ('app_id', 'app_name', 'icon_url', 'app_title', 'app_description', 'version', 'file_size', 'downloads', 'view_url', 'created', 'updated')


class UserPinnedAppSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserPinnedApps
		fields = ('id', 'user', 'app', 'lon', 'lat', 'created')


class UserBlockedAppSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserBlockedApps
		fields = ('id', 'user', 'app', 'created')
		

class UserSharedAppSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserSharedApps
		fields = ('id', 'user', 'app', 'lon', 'lat', 'created')
		

class AppDetailsSerializer(serializers.ModelSerializer):

	class Meta:
		model = AppDetails
		fields = ('id', 'app', 'language_code', 'title', 'description', 'screenshots', 'video', 'company_url', 'support_url', 'release_notes', 'created', 'updated')
		
		
class AppDeviceTypeSerializer(serializers.ModelSerializer):

	class Meta:
		model = AppDeviceType
		fields = ('id', 'app_id', 'device_type_id')
		
		
class DeviceTypeSerializer(serializers.ModelSerializer):

	class Meta:
		model = DeviceType
		fields = ('device_id', 'name')
		
		
class AppPriceSerializer(serializers.ModelSerializer):

	class Meta:
		model = AppPrice
		fields = ('app_id', 'storefront_id', 'retail_price', 'currency_code')