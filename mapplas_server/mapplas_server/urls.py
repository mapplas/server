from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('rest_api.views',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # API url
    url(r'^api/city/(?P<city_id>\d+)/$', 'api_apps_for_city'),
	url(r'^api/position/lat=(?P<lat>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)&lon=(?P<lon>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)&acc=(?P<accuracy>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)/$', 'api_apps_for_position'),
  
)
