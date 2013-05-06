from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

from rest_api.models import User, Application, UserPinnedApps, UserBlockedApps, UserSharedApps, AppDetails
from rest_api.serializers import UserSerializer, ApplicationSerializer, UserPinnedAppSerializer, UserBlockedAppSerializer, UserSharedAppSerializer, AppDetailsSerializer
	
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
				return Response(serializer.data, status=status.HTTP_200_OK)
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


@csrf_exempt
@api_view(['POST'])	
def app_block_unblock(request):
	'''
	Blocks or unblocks an app for a concrete user.
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
				
				if action=='block':
					try:
						blockedApp = UserBlockedApps.objects.get(app_id=appId, user_id=userId)
						error = {}
						error['error'] = 'Application already blocked'
						return Response(error, status=status.HTTP_400_BAD_REQUEST)
						
					except UserBlockedApps.DoesNotExist:
						'''
						Create object to be serialized
						'''
						dataToSerialize = {}
						dataToSerialize['user'] = userId
						dataToSerialize['app'] = appId
						dataToSerialize['created'] = timezone.now()
						
						serializer = UserBlockedAppSerializer(data=dataToSerialize)
						
						if serializer.is_valid():
							serializer.save()
							return Response(serializer.data, status=status.HTTP_201_CREATED)
						else:
							return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
				
				elif action=='unblock':
					'''
					Delete object from db
					'''
					try:
						blockedApp = UserBlockedApps.objects.get(app_id=appId, user_id=userId)
						blockedApp.delete()
					
						info = {}
						info['info'] = 'OK'
						return Response(info, status=status.HTTP_201_CREATED)
						
					except UserBlockedApps.DoesNotExist:
						error = {}
						error['error'] = 'Application was not blocked before'
						return Response(error, status=status.HTTP_400_BAD_REQUEST)
				
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
			

@csrf_exempt
@api_view(['POST'])	
def app_share(request):
	'''
	Shares of an application of a concrete user in a concrete location.
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
				Create object to be serialized
				'''
				dataToSerialize = {}
				dataToSerialize['user'] = userId
				dataToSerialize['app'] = appId
				dataToSerialize['lon'] = data['lon']
				dataToSerialize['lat'] = data['lat']
				dataToSerialize['created'] = timezone.now()
						
				serializer = UserSharedAppSerializer(data=dataToSerialize)
						
				if serializer.is_valid():
					serializer.save()
					return Response(serializer.data, status=status.HTTP_201_CREATED)
				else:
					return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
							
			except Application.DoesNotExist:
				error = {}
				error['error'] = 'Application does not exist for id %s' % appId
				return Response(error, status=status.HTTP_400_BAD_REQUEST)
			
		except User.DoesNotExist:
			error = {}
			error['error'] = 'User does not exist for id %s' % userId
			return Response(error, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def app_detail(request, app_id):
	'''
	Returns the detail of the requested app
	'''
	if request.method == 'POST':
		data = request.POST
		
		'''
		Get language
		'''
		lang = data['l']
		
		'''
		Get application
		'''
		try:
			app = Application.objects.get(pk=app_id)
			
			try:
				'''
				Get Application detail for given language
				'''
				appDetail = AppDetails.objects.get(app_id=app.app_id, language_code=lang)
				serializer = AppDetailsSerializer(appDetail)
				
				return Response(serializer.data, status=status.HTTP_200_OK)
				
			except AppDetails.DoesNotExist:
				'''
				Application detail for given language does not exist
				'''
				try:
					'''
					Return any other app detail
					'''
					appDetail = AppDetails.objects.all().filter(app_id=app.app_id)
					serializer = AppDetailsSerializer(appDetail[0])
										
					return Response(serializer.data, status=status.HTTP_200_OK)
					
				except AppDetails.DoesNotExist:
					error = {}
					error['error'] = 'ApplicationDetail does not exist for id %s' % app_id
					return Response(error, status=status.HTTP_400_BAD_REQUEST)
			
		except Application.DoesNotExist:
			error = {}
			error['error'] = 'Application does not exist for id %s' % app_id
			return Response(error, status=status.HTTP_400_BAD_REQUEST)
			

@csrf_exempt
@api_view(['POST'])
def user_apps(request, user_id):
	'''
	Returns user blocked and pinned apps
	'''
	if request.method == 'POST':
		data = request.POST
		
		'''
		Get user
		'''
		try:
			user = User.objects.get(pk=user_id)
			
			'''
			Get pinned apps for user
			'''
			pinnedApps = UserPinnedApps.objects.all().filter(user_id=user_id)
			pinnedAppsSerializer = UserPinnedAppSerializer(pinnedApps, many=True)

			'''
			Get blocked apps for user
			'''
			blockedApps = UserBlockedApps.objects.all().filter(user_id=user_id)
			blockedAppsSerializer = UserBlockedAppSerializer(blockedApps, many=True)
			
			'''
			Add blocked and pinned apps
			'''
			response = {}
			response['pinned'] = pinnedAppsSerializer.data
			response['blocked'] = blockedAppsSerializer.data
			
			return Response(response, status=status.HTTP_200_OK)
			
		except User.DoesNotExist:
			error = {}
			error['error'] = 'User does not exist for id %s' % user_id
			return Response(error, status=status.HTTP_400_BAD_REQUEST)