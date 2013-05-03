from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_api.models import User, Application, UserPinnedApps
from rest_api.serializers import UserSerializer, ApplicationSerializer, UserPinnedAppSerializer
	
@csrf_exempt
@api_view(['POST'])
def user_register(request):
	'''
	If user does not exists, saves it.
	Else, returns its data from db.
	'''
	if request.method == 'POST':
		data = request.POST
			
		try:
			'''
			Update database user
			'''
			user = User.objects.get(imei=data['imei'])
			
			dataToSave = {}
			dataToSave['updated'] = timezone.now()
			
			serializer = UserSerializer(user, data=dataToSave, partial=True)
			
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except User.DoesNotExist:
			'''
			User does not exists into db. Insert.
			'''
			data['created'] = timezone.now()
			data['updated'] = timezone.now()
					
			serializer = UserSerializer(data=data)
			
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])	
def app_pin_unpin(request):
	'''
	Pins or unpins an app for a concrete user in a concrete location.
	'''
	if request.method == 'POST':
		data = request.POST
		
		try:
			'''	
			Get user
			'''
			user = User.objects.get(id=data['uid'])
			print('User exists')			
			
			try:
				'''
				Get application
				'''
				app = Application.objects.get(app_id=data['app'])
				print('App exists')
				
			except Application.DoesNotExist:
				error = {'appId' : 'Application does not exist'}
				print('App NOT exists')
				return Response(error, status=status.HTTP_400_BAD_REQUEST)
			
		except User.DoesNotExist:
			error = {'userId' : 'User does not exist'}
			print('User NOT exists')
			return Reponse(error, status=status.HTTP_400_BAD_REQUEST)
	
		