from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/user/add/$', 'rest_api.views.user_register'),
    
    url(r'^api/apps/$', 'rest_api.views.applications'),
    
    url(r'^api/user/pin/$', 'rest_api.views.app_pin_unpin'),
    url(r'^api/user/block/$', 'rest_api.views.app_block_unblock'),
    url(r'^api/user/share/$', 'rest_api.views.app_share'),
    
    url(r'^api/app-detail/(?P<app_id>[a-zA-Z0-9_.]+)/$', 'rest_api.views.app_detail'),
    
    url(r'^api/user-apps-info/(?P<user_id>\d+)/$', 'rest_api.views.user_apps'),
    
    url(r'^api/installed-apps/$', 'rest_api.views.installed_apps'),
)
