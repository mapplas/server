from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/user/add$', 'rest_api.views.user_register'),
    url(r'^api/user/pin$', 'rest_api.views.app_pin_unpin'),
    url(r'^api/user/block$', 'rest_api.views.app_block_unblock'),
)
