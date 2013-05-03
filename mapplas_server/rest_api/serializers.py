from django.forms import widgets
from django.utils import timezone
from rest_framework import serializers
from rest_api.models import User, Application, UserPinnedApps, UserBlockedApps, UserSharedApps

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