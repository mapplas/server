from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import get_cache


class CustomAnonRateThrottle(AnonRateThrottle):
	cache = get_cache('throttle-anon')
	rate = '1000/day'


class CustomUserRateThrottle(UserRateThrottle):
	cache = get_cache('throttle-user')
	rate = '5000/day'