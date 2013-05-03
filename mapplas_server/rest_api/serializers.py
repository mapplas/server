from django.forms import widgets
from django.utils import timezone
from rest_framework import serializers
from rest_api.models import User

class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('imei', 'tel', 'created', 'updated', 'id')