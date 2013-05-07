from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

from rest_api.models import User, Application, UserPinnedApps, UserBlockedApps, UserSharedApps, AppDetails
from rest_api.serializers import UserSerializer, ApplicationSerializer, UserPinnedAppSerializer, UserBlockedAppSerializer, UserSharedAppSerializer, AppDetailsSerializer
from rest_api.errors import ResponseGenerator
	
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
				
				'''
				Return only useful values
				'''
				returnJson = {}
				returnJson['user'] = user.id
				returnJson['imei'] = user.imei
				returnJson['tel'] = user.tel
				
				return ResponseGenerator.ok_with_message(returnJson)
			else:
				return ResponseGenerator.serializer_error(serializer.errors)

		except User.DoesNotExist:
			'''
			User does not exists into db. Insert.
			'''
			data['created'] = timezone.now()
			data['updated'] = timezone.now()
					
			serializer = UserSerializer(data=data)
			
			if serializer.is_valid():
				serializer.save()
				
				'''
				Return only useful values
				'''
				userImei = data['imei']
				user = User.objects.get(imei=data['imei'])
				
				returnJson = {}
				returnJson['user'] = user.id
				returnJson['imei'] = user.imei
				returnJson['tel'] = user.tel
				
				return ResponseGenerator.ok_with_message(returnJson)
			else:
				return ResponseGenerator.serializer_error(serializer.errors)

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
						
						return ResponseGenerator.generic_error('Application already pinned')
						
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
							
							return ResponseGenerator.ok_response()
						else:
							return ResponseGenerator.serializer_error(serializer.errors)
							
				elif action=='unpin':
					'''
					Delete object from db
					'''
					try:
						pinnedApp = UserPinnedApps.objects.get(app_id=appId, user_id=userId)
						pinnedApp.delete()
						
						return ResponseGenerator.ok_response()
						
					except UserPinnedApps.DoesNotExist:
						return ResponseGenerator.generic_error('Application was not pinned before')
					
				else:
					return ResponseGenerator.unsupported_action_error(action)
					
			except Application.DoesNotExist:
				return ResponseGenerator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return ResponseGenerator.user_not_exist_error(userId)


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
						
						return ResponseGenerator.generic_error('Application already blocked')
						
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
							
							return ResponseGenerator.ok_response()
						else:
							return ResponseGenerator.serializer_error(serializer.errors)
				
				elif action=='unblock':
					'''
					Delete object from db
					'''
					try:
						blockedApp = UserBlockedApps.objects.get(app_id=appId, user_id=userId)
						blockedApp.delete()
					
						return ResponseGenerator.ok_response()
						
					except UserBlockedApps.DoesNotExist:
						return ResponseGenerator.generic_error('Application was not blocked before')
				
				else:
					return ResponseGenerator.unsupported_action_error(action)
				
			except Application.DoesNotExist:
				return ResponseGenerator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return ResponseGenerator.user_not_exist_error(userId)
			

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
					
					return ResponseGenerator.ok_response()
					
				else:
					return ResponseGenerator.serializer_error(serializer.errors)
							
			except Application.DoesNotExist:
				return ResponseGenerator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return ResponseGenerator.user_not_exist_error(userId)


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
				
				return ResponseGenerator.ok_with_message(serializer.data)
				
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
										
					return ResponseGenerator.ok_with_message(serializer.data)
					
				except AppDetails.DoesNotExist:
					return ResponseGenerator.generic_error_param('ApplicationDetail does not exist for id', app_id)
			
		except Application.DoesNotExist:
			return ResponseGenerator.app_not_exist_error(app_id)

			

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
			Get pinned apps for user (id, name, logo, lat, lon)
			'''
			pinnedApps = UserPinnedApps.objects.all().filter(user_id=user_id)

			response = {}
			pinnedArray = []
			pinnedAppsResponse = {}
			
			for pinnedApp in pinnedApps:
				pinnedAppsResponse['id'] = pinnedApp.app.app_id
				pinnedAppsResponse['name'] = pinnedApp.app.app_name
				pinnedAppsResponse['icon'] = pinnedApp.app.icon_url
				pinnedArray.append(pinnedAppsResponse.copy())
				
			response['pinned'] = pinnedArray

			'''
			Get blocked apps for user (id, name, logo)
			'''
			blockedApps = UserBlockedApps.objects.all().filter(user_id=user_id)
			
			blockedArray = []
			blockedAppsResponse = {}
			
			for blockedApp in blockedAppsResponse:
				blockedAppsResponse['id'] = blocked.app.app_id
				blockedAppsResponse['name'] = blocked.app.app_name
				blockedAppsResponse['icon'] = blocked.app.icon_url
				blockedArray.append(blockedAppsResponse.copy())
			
			response['blocked'] = blockedArray
			
			return ResponseGenerator.ok_with_message(response)
			
		except User.DoesNotExist:
			return ResponseGenerator.user_not_exist_error(userId)
			

@csrf_exempt
@api_view(['POST'])
def installed_apps(request):
	'''
	Returns all avaliable url scheme for given store
	'''
	if request.method == 'POST':
		
		'''
		Get all applications with url scheme
		'''
		appQuery = Application.objects.all().filter().exclude(url_schema__isnull=True)
		
		appsWithScheme = {}
		appsWithSchemeArray = []
		
		for app in appQuery:
			appsWithScheme['i'] = app.app_id
			appsWithScheme['s'] = app.url_schema
			appsWithSchemeArray.append(appsWithScheme.copy())
			
		return ResponseGenerator.ok_with_message(appsWithSchemeArray)
			
			