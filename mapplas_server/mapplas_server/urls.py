from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mapplas_server.views.home', name='home'),
    # url(r'^mapplas_server/', include('mapplas_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/user/add', 'rest_api.views.user_register'),
    url(r'^api/user/pin', 'rest_api.views.app_pin_unpin'),
    #url(r'^users/(?P<pk>[0-9]+)/$', 'mapplas_server.views.user_detail'),
)
