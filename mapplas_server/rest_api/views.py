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
			userId = data['uid']
			user = User.objects.get(id=userId)
			
			try:
				'''
				Get application
				'''
				appId = data['app']
				app = Application.objects.get(app_id=appId)
				
				
				'''
				Get request action
				'''
				action = data['s']
				print(action)
				
				if action=='pin':
					'''
					Check if app was pinned before
					'''
					try:
						pinnedApp = UserPinnedApps.objects.get(app_id=appId, user_id=userId)
						
						error = {}
						error['error'] = 'Application already pinned'
						return Response(error, status=status.HTTP_400_BAD_REQUEST)
						
					except UserPinnedApps.DoesNotExist:
						'''
						Create object to be serialized
						'''
						dataToSerialize = {}
						dataToSerialize['user'] = userId
						dataToSerialize['app'] = appId
						dataToSerialize['lon'] = data['lon']
						dataToSerialize['lat'] = data['lat']
						dataToSerialize['created'] = timezone.now()
						
						serializer = UserPinnedAppSerializer(data=dataToSerialize)
						
						if serializer.is_valid():
							serializer.save()
							return Response(serializer.data, status=status.HTTP_201_CREATED)
						else:
							return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
							
				elif action=='unpin':
					'''
					Delete object from db
					'''
					try:
						pinnedApp = UserPinnedApps.objects.get(app_id=appId, user_id=userId)
						pinnedApp.delete()
					
						info = {}
						info['info'] = 'OK'
						return Response(info, status=status.HTTP_201_CREATED)
						
					except UserPinnedApps.DoesNotExist:
						error = {}
						error['error'] = 'Application was not pinned before'
						return Response(error, status=status.HTTP_201_CREATED)
					
				else:
					error = {}
					error['error'] = 'Unsupported action %s' % action
					return Response(error, status=status.HTTP_400_BAD_REQUEST)
					
			except Application.DoesNotExist:
				error = {}
				error['error'] = 'Application does not exist for id %s' % appId
				return Response(error, status=status.HTTP_400_BAD_REQUEST)
			
		except User.DoesNotExist:
			error = {}
			error['error'] = 'User does not exist for id %s' % userId
			return Response(error, status=status.HTTP_400_BAD_REQUEST)
	
		