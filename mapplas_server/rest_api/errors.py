from rest_framework import status
from rest_framework.response import Response

from rest_api.error_enum import ErrorKeys

class ResponseGenerator:
	
	def user_not_exist_error(user_id):
		error = {}
		error[ErrorKeys.ERROR] = 'User does not exist for id %s' % user_id
		return Response(error, status=status.HTTP_400_BAD_REQUEST)
	
	
	def app_not_exist_error(app_id):
		error = {}
		error[ErrorKeys.ERROR] = 'Application does not exist for id %s' % app_id
		return Response(error, status=status.HTTP_400_BAD_REQUEST)
		
		
	def unsupported_action_error(action):
		error = {}
		error[ErrorKeys.ERROR] = 'Unsupported action %s' % action
		return Response(error, status=status.HTTP_400_BAD_REQUEST)
		
		
	def generic_error(message):
		error = {}
		error[ErrorKeys.ERROR] = message
		return Response(error, status=status.HTTP_400_BAD_REQUEST)
		
		
	def generic_error_param(message, param):
		error = {}
		error[ErrorKeys.ERROR] = message  + ' %s' % param
		return Response(error, status=status.HTTP_400_BAD_REQUEST)
		
		
	def serializer_error(serializer_error):
		return Response(serializer_error, status=status.HTTP_400_BAD_REQUEST)
		
		
	def serializer_ok(serializer_msg):
		return Response(serializer_msg, status=status.HTTP_201_CREATED)
		
	
	def ok_response():
		info = {}
		info[ErrorKeys.INFO] = 'OK'
		return Response(info, status=status.HTTP_200_OK)
	