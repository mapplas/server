from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('rest_api.views',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
#     url(r'^api/user/add/$', 'user_register'),
#     
#     url(r'^api/apps/(?P<multiple>\d+)/$', 'applications'),
#     
#     url(r'^api/user/pin/$', 'app_pin_unpin'),
#     url(r'^api/user/block/$', 'app_block_unblock'),
#     url(r'^api/user/share/$', 'app_share'),
#     
#     url(r'^api/app-detail/(?P<app_id>[a-zA-Z0-9_.]+)/$', 'app_detail'),
#     
#     url(r'^api/user-apps-info/(?P<user_id>\d+)/$', 'user_apps'),
#     
#     url(r'^api/installed-apps/$', 'installed_apps'),
#     
#     url(r'^api/user/app-interaction/$', 'user_appstore_interaction'),
)
