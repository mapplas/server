from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

from rest_api.models import User, Application, UserPinnedApps, UserBlockedApps, UserSharedApps, AppDetails, AppDeviceType, DeviceType, AppPrice
from rest_api.serializers import UserSerializer, ApplicationSerializer, UserPinnedAppSerializer, UserBlockedAppSerializer, UserSharedAppSerializer, AppDetailsSerializer, AppDeviceTypeSerializer
from rest_api.errors import ResponseGenerator
	
@csrf_exempt
@api_view(['POST'])
def user_register(request):
	'''
	If user does not exists, saves it.
	Else, returns its data from db.
	'''
	if request.method == 'POST':
		data = request.DATA
			
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
def applications(request, multiple):
	'''
	Gets application list
	'''
	if request.method == 'POST':
		data = request.DATA
		
		lat = data['lat']
		lon = data['lon']
		accuracy = data['p']

		response = {}
		appsArray = []
		appsDict = {}
		
		try:
			'''
			Get user
			'''
			user_id = data['uid']
			user = User.objects.get(pk=user_id)
						
			'''
			Get UserPinnedApps
			'''
			try:
				userPinnedApps = UserPinnedApps.objects.all().filter(user_id=user_id)
				
			except UserPinnedApps.DoesNotExist:
				'''
				Do nothing
				'''
			
			apps = Application.objects.all()
			
			'''
			If multiple = 0, get first 25 (0*25=0 -> from 0 to 25) apps
			If multiple = 1, get next 25 (1*25=25 -> from 25 to 50) apps
			'''
			
			for app in apps:
				appsDict['id'] = app.app_id
				appsDict['n'] = app.app_name
				appsDict['i'] = app.icon_url
				appsDict['sc'] = app.url_schema
				appsDict['asid'] = app.app_id_appstore
				
				'''
				Check if app is blocked by user
				'''
				try:
					appIsBlocked = UserBlockedApps.objects.get(user_id=user_id, app_id=app.app_id)
					continue
					
				except UserBlockedApps.DoesNotExist:
					'''
					Do nothing
					'''
				
				'''
				Check if app is pinned by user
				'''
				try:
					appIsPinned = userPinnedApps.get(app_id=app.app_id)
					appsDict['pin'] = 1

				except UserPinnedApps.DoesNotExist:
					appsDict['pin'] = 0
					
				'''
				Check number of pins for this app
				'''
				try:
					appsDict['tpin'] = UserPinnedApps.objects.all().filter(app_id=app.app_id).count()
					
				except UserPinnedApps.DoesNotExist:
					appsDict['tpin'] = 0
					
				'''
				Check app type. MUST exist for all apps
				'''
				try:
					appDeviceType = AppDeviceType.objects.get(app_id=app.app_id)
					appsDict['type'] = appDeviceType.device_type.name
				
				except AppDeviceType.DoesNotExist:
					return ResponseGenerator.generic_error_param('App device type does not exist for app', app.app_id)
					
				'''
				Check app price, storefront and currency code
				App price, 0 or float.
				Storefront: 1 Spanish Appstore, 2 American Appstore
				Currency Code, ISO codes: EUR for euro, USD for United States dollar
				'''
				storefront_id = 2
				try:
					appsDict['pr'] = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id).retail_price
					appsDict['cu'] = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id).currency_code
					appsDict['st'] = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id).storefront_id
				
				except AppPrice.DoesNotExist:
					'''
					HTML5 app
					'''
				
				appsArray.append(appsDict.copy())
				appsArray.append(appsDict.copy())
				
			response['apps'] = appsArray
			response['last'] = 1
			
			return ResponseGenerator.ok_with_message(response)
			
		except User.DoesNotExist:
			'''
			Return error response
			'''
			return ResponseGenerator.user_not_exist_error(user_id)


@csrf_exempt
@api_view(['POST'])	
def app_pin_unpin(request):
	'''
	Pins or unpins an app for a concrete user in a concrete location.
	'''
	if request.method == 'POST':
		data = request.DATA
		
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
		data = request.DATA
		
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
		data = request.DATA
		
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
				dataToSerialize['via'] = data['via']
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
		data = request.DATA
		
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
				
				return ResponseGenerator.ok_with_message(serializeAppDetail(appDetail))
				
			except AppDetails.DoesNotExist:
				'''
				Application detail for given language does not exist
				'''
				try:
					'''
					Return any other app detail
					'''
					appDetail = AppDetails.objects.all().filter(app_id=app.app_id)
					
					return ResponseGenerator.ok_with_message(serializeAppDetail(appDetail))
					
				except AppDetails.DoesNotExist:
					return ResponseGenerator.generic_error_param('ApplicationDetail does not exist for id', app_id)
			
		except Application.DoesNotExist:
			return ResponseGenerator.app_not_exist_error(app_id)


def serializeAppDetail(app_detail):
	appDetailToReturn = {}
	
	appDetailToReturn ['d'] = app_detail.description
	appDetailToReturn ['scr'] = app_detail.screenshots
	#appDetailToReturn ['v'] = app_detail.video
	appDetailToReturn ['curl'] = app_detail.company_url
	appDetailToReturn ['surl'] = app_detail.support_url
	
	return appDetailToReturn
	

@csrf_exempt
@api_view(['POST'])
def user_apps(request, user_id):
	'''
	Returns user blocked and pinned apps
	'''
	if request.method == 'POST':
		data = request.DATA
		
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
				pinnedAppsResponse['n'] = pinnedApp.app.app_name
				pinnedAppsResponse['i'] = pinnedApp.app.icon_url
				pinnedArray.append(pinnedAppsResponse.copy())
				
			response['pinned'] = pinnedArray

			'''
			Get blocked apps for user (id, name, logo)
			'''
			blockedApps = UserBlockedApps.objects.all().filter(user_id=user_id)
			
			blockedArray = []
			blockedAppsResponse = {}
			
			for blockedApp in blockedApps:
				blockedAppsResponse['id'] = blockedApp.app.app_id
				blockedAppsResponse['n'] = blockedApp.app.app_name
				blockedAppsResponse['i'] = blockedApp.app.icon_url
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
			
			