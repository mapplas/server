# -*- encoding: utf-8 -*-
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

from rest_api import helper, application_searcher
from rest_api.error_enum import AppListSize
	
@csrf_exempt
@api_view(['POST'])
def user_register(request):
	'''
	If user does not exists, saves it.
	Else, returns its data from db.
	'''
	if request.method == 'POST':
		data = request.DATA
		responseGenerator = ResponseGenerator()
			
		try:
			'''
			Update database user
			'''
			user = User.objects.get(imei=data['imei'])
			
			dataToSave = {}
			dataToSave['updated'] = helper.epoch(timezone.now())
			
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
				
				return responseGenerator.ok_with_message(returnJson)
			else:
				return responseGenerator.serializer_error(serializer.errors)

		except User.DoesNotExist:
			'''
			User does not exists into db. Insert.
			'''
			data['created'] = helper.epoch(timezone.now())
			data['updated'] = helper.epoch(timezone.now())
					
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
				
				return responseGenerator.ok_with_message(returnJson)
			else:
				return responseGenerator.serializer_error(serializer.errors)


@csrf_exempt
@api_view(['POST'])
def applications(request, multiple):
	'''
	Gets application list
	'''
	if request.method == 'POST':
		data = request.DATA
		
		response_generator = ResponseGenerator()
		
		lat = data['lat']
		lon = data['lon']
		accuracy = data['p']
		lang = data['l']

		response = {}
		appsArray = []
		appsDict = {}
		
		try:
			'''
			Get user
			'''
			user_id = data['uid']
			user = User.objects.get(pk=user_id)
			
			apps_ok_to_user = application_searcher.search(lat, lon, accuracy, user_id)
			
			'''
			If multiple = 0, get first 25 (0*25=0 -> from 0 to 25) apps
			If multiple = 1, get next 25 (1*25=25 -> from 25 to 50) apps
			'''
			from_app = int(int(multiple) * int(AppListSize.SIZE_OF_LIST))
			to_app = int(from_app + int(AppListSize.SIZE_OF_LIST))

			apps_ok_to_user_length = len(apps_ok_to_user)

			if (to_app - 1 >= apps_ok_to_user_length):
				to_app = apps_ok_to_user_length
				
			apps = apps_ok_to_user[from_app:to_app]
			
			userPinnedApps = UserPinnedApps.objects.filter(user_id=user_id)
			
			for app in apps:
			
				appsDict['id'] = app.app_id_appstore
				appsDict['n'] = app.app_name
				appsDict['i'] = app.icon_url
				appsDict['sc'] = app.url_schema
				
				'''
				Get app description first 100 chars
				'''
				description = get_app_description(lang, app)
				appsDict['sd'] = description[:100]
				
				'''
				Check if app is pinned by user
				'''
				try:

					appIsPinned = userPinnedApps.get(app_id=app.app_id_appstore)
					appsDict['pin'] = 1

				except UserPinnedApps.DoesNotExist:
					appsDict['pin'] = 0
					
				'''
				Check number of pins for this app
				'''
				try:
					appsDict['tpin'] = UserPinnedApps.objects.all().filter(app_id=app.app_id_appstore).count()
					
				except UserPinnedApps.DoesNotExist:
					appsDict['tpin'] = 0
					
				'''
				Check app type. MUST exist for all apps
				'''
				#try:
				#	appDeviceType = AppDeviceType.objects.get(app_id=app.app_id_appstore)
				#	appsDict['type'] = appDeviceType.device_type.name
				
				#except AppDeviceType.DoesNotExist:
				#	return ResponseGenerator.generic_error_param('App device type does not exist for app', app.app_id_appstore)
					
				'''
				Check app price, storefront and currency code
				App price, 0 or float.
				Storefront: 143454 Spanish Appstore, 143441 American Appstore
				Currency Code, ISO codes: EUR for euro, USD for United States dollar
				'''
				storefront_id = 143454
				try:
					appsDict['pr'] = AppPrice.objects.get(app_id=app.app_id_appstore, storefront_id=storefront_id).retail_price
					appsDict['cu'] = AppPrice.objects.get(app_id=app.app_id_appstore, storefront_id=storefront_id).currency_code
					appsDict['st'] = AppPrice.objects.get(app_id=app.app_id_appstore, storefront_id=storefront_id).storefront_id
					
					appsArray.append(appsDict.copy())
					
				except AppPrice.DoesNotExist:
					'''
					App does not exist on that appstore
					Do not add app to dictionary
					'''
					
				
			response['apps'] = appsArray
			
			# Check if user can request for more apps
			if (to_app == apps_ok_to_user_length):
				response['last'] = 1
			else:
				response['last'] = 0
			
			return response_generator.ok_with_message(response)
			
		except User.DoesNotExist:
			'''
			Return error response
			'''
			return response_generator.user_not_exist_error(user_id)


@csrf_exempt
@api_view(['POST'])	
def app_pin_unpin(request):
	'''
	Pins or unpins an app for a concrete user in a concrete location.
	'''
	if request.method == 'POST':
		data = request.DATA
		response_generator = ResponseGenerator()
		
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
				app = Application.objects.get(app_id_appstore=appId)
				
				
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
						
						return response_generator.generic_error('Application already pinned')
						
					except UserPinnedApps.DoesNotExist:
						'''
						Create object to be serialized
						'''
						dataToSerialize = {}
						dataToSerialize['user'] = userId
						dataToSerialize['app'] = appId
						dataToSerialize['lon'] = data['lon']
						dataToSerialize['lat'] = data['lat']
						dataToSerialize['created'] = helper.epoch(timezone.now())
						
						serializer = UserPinnedAppSerializer(data=dataToSerialize)
						
						if serializer.is_valid():
							serializer.save()
							
							return response_generator.ok_response()
						else:
							return response_generator.serializer_error(serializer.errors)
							
				elif action=='unpin':
					'''
					Delete object from db
					'''
					try:
						pinnedApp = UserPinnedApps.objects.get(app_id=appId, user_id=userId)
						pinnedApp.delete()
						
						return response_generator.ok_response()
						
					except UserPinnedApps.DoesNotExist:
						return response_generator.generic_error('Application was not pinned before')
					
				else:
					return response_generator.unsupported_action_error(action)
					
			except Application.DoesNotExist:
				return response_generator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return response_generator.user_not_exist_error(userId)


@csrf_exempt
@api_view(['POST'])	
def app_block_unblock(request):
	'''
	Blocks or unblocks an app for a concrete user.
	'''
	if request.method == 'POST':
		data = request.DATA
		response_generator = ResponseGenerator()
		
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
				app = Application.objects.get(app_id_appstore=appId)
				
				
				'''
				Get request action
				'''
				action = data['s']
				
				if action=='block':
					try:
						blockedApp = UserBlockedApps.objects.get(app_id=appId, user_id=userId)
						
						return response_generator.generic_error('Application already blocked')
						
					except UserBlockedApps.DoesNotExist:
						'''
						Create object to be serialized
						'''
						dataToSerialize = {}
						dataToSerialize['user'] = userId
						dataToSerialize['app'] = appId
						dataToSerialize['created'] = helper.epoch(timezone.now())
						
						serializer = UserBlockedAppSerializer(data=dataToSerialize)
						
						if serializer.is_valid():
							serializer.save()
							
							return response_generator.ok_response()
						else:
							return response_generator.serializer_error(serializer.errors)
				
				elif action=='unblock':
					'''
					Delete object from db
					'''
					try:
						blockedApp = UserBlockedApps.objects.get(app_id=appId, user_id=userId)
						blockedApp.delete()
					
						return response_generator.ok_response()
						
					except UserBlockedApps.DoesNotExist:
						return response_generator.generic_error('Application was not blocked before')
				
				else:
					return response_generator.unsupported_action_error(action)
				
			except Application.DoesNotExist:
				return response_generator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return response_generator.user_not_exist_error(userId)
			

@csrf_exempt
@api_view(['POST'])	
def app_share(request):
	'''
	Shares of an application of a concrete user in a concrete location.
	'''
	if request.method == 'POST':
		data = request.DATA
		response_generator = ResponseGenerator()
		
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
				app = Application.objects.get(app_id_appstore=appId)
				
				'''
				Create object to be serialized
				'''
				dataToSerialize = {}
				dataToSerialize['user'] = userId
				dataToSerialize['app'] = appId
				dataToSerialize['lon'] = data['lon']
				dataToSerialize['lat'] = data['lat']
				dataToSerialize['via'] = data['via']
				dataToSerialize['created'] = helper.epoch(timezone.now())
						
				serializer = UserSharedAppSerializer(data=dataToSerialize)
						
				if serializer.is_valid():
					serializer.save()
					
					return response_generator.ok_response()
					
				else:
					return response_generator.serializer_error(serializer.errors)
							
			except Application.DoesNotExist:
				return response_generator.app_not_exist_error(appId)
			
		except User.DoesNotExist:
			return response_generator.user_not_exist_error(userId)


@csrf_exempt
@api_view(['POST'])
def app_detail(request, app_id):
	'''
	Returns the detail of the requested app
	'''
	if request.method == 'POST':
		data = request.DATA
		response_generator = ResponseGenerator()
		
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
				appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code=lang.upper())
				return response_generator.ok_with_message(serializeAppDetail(appDetail))
				
			except AppDetails.DoesNotExist:
				'''
				Application detail for given language does not exist
				
				Try with english version of app description
				'''
				try:
					appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code='EN')
					return response_generator.ok_with_message(serializeAppDetail(appDetail))
					
				except AppDetails.DoesNotExist:
					'''
					Try with spanish version of app description
					'''
					try:
						appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code='ES')
						return response_generator.ok_with_message(serializeAppDetail(appDetail))
						
					except AppDetails.DoesNotExist:
						'''
						Return application default description
						'''
						appDetailToReturn = {}
						appDetailToReturn ['d'] = app.app_description
						appDetailToReturn ['curl'] = app.company_url
						appDetailToReturn ['surl'] = app.support_url
						
						return response_generator.ok_with_message(appDetailToReturn)
					
				except AppDetails.DoesNotExist:
					return response_generator.generic_error_param('ApplicationDetail does not exist for id', app_id)
			
		except Application.DoesNotExist:
			return response_generator.app_not_exist_error(app_id)

def get_app_description(lang, app):
	
	try:
		'''
		Get Application detail for given language
		'''
		appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code=lang.upper())
		return appDetail.description

	except AppDetails.DoesNotExist:
		'''
		Application detail for given language does not exist
		
		Try with english version of app description
		'''
		try:
			appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code='EN')
			return appDetail.description
			
		except AppDetails.DoesNotExist:
			'''
			Try with spanish version of app description
			'''
			try:
				appDetail = AppDetails.objects.get(app_id=app.app_id_appstore, language_code='ES')
				return appDetail.description
				
			except AppDetails.DoesNotExist:
				'''
				Return application default description
				'''
				return app.app_description


def serializeAppDetail(app_detail):
	
	appDetailToReturn = {}
	screenshots = []
	if app_detail.screenshot1:
		screenshots.append(app_detail.screenshot1)
	
	if app_detail.screenshot2:	
		screenshots.append(app_detail.screenshot2)
	
	if app_detail.screenshot3:
		screenshots.append(app_detail.screenshot3)

	if app_detail.screenshot4:
		screenshots.append(app_detail.screenshot4)
	
	appDetailToReturn ['d'] = app_detail.description
	appDetailToReturn ['scr'] = screenshots
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
		response_generator = ResponseGenerator()
		
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
				pinnedAppsResponse['id'] = pinnedApp.app.app_id_appstore
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
				blockedAppsResponse['id'] = blockedApp.app.app_id_appstore
				blockedAppsResponse['n'] = blockedApp.app.app_name
				blockedAppsResponse['i'] = blockedApp.app.icon_url
				blockedArray.append(blockedAppsResponse.copy())
			
			response['blocked'] = blockedArray
						
			return response_generator.ok_with_message(response)
			
		except User.DoesNotExist:
			return response_generator.user_not_exist_error(user_id)
			

@csrf_exempt
@api_view(['POST'])
def installed_apps(request):
	'''
	Returns all avaliable url scheme for given store
	'''
	if request.method == 'POST':
		response_generator = ResponseGenerator()
		
		'''
		Get all applications with url scheme
		'''
		appQuery = Application.objects.all().filter().exclude(url_schema__isnull=True)
		
		appsWithScheme = {}
		appsWithSchemeArray = []
		
		for app in appQuery:
			appsWithScheme['i'] = app.app_id_appstore
			appsWithScheme['s'] = app.url_schema
			appsWithSchemeArray.append(appsWithScheme.copy())
			
		return response_generator.ok_with_message(appsWithSchemeArray)