from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_api.models import User
from rest_api.serializers import UserSerializer
	
@csrf_exempt
@api_view(['POST'])
def user_register(request):
	'''
	If user does not exists, saves it.
	Else, returns its data from db.
	'''
	if request.method == 'POST':
		data = request.POST
				
		data['created'] = timezone.now()
		data['updated'] = timezone.now()
				
		serializer = UserSerializer(data=data)
		
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		
'''		
@csrf_exempt
def user_list(request):
	
	if request.method == 'GET':
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		return JSONResponse(serializer.data)
	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = UserSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		else:
			return JSONResponse(serializer.errors, status=400)
            
            
@csrf_exempt
def user_detail(request, pk):
	
	try:
		snippet = User.objects.get(pk=pk)
	except User.DoesNotExist:
		return HttpResponse(status=404)
		
	if request.method == 'GET':
		serializer = UserSerializer(snippet)
		return JSONResponse(serializer.data)
	
	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = UserSerializer(snippet, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		else:
			return JSONResponse(serializer.errors, status=400)
		
	elif request.method == 'DELETE':
		snippet.delete()
		return HttpResponse(status=204)
'''