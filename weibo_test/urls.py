from django.conf.urls import patterns, include, url
from weibo_test.views import login,test

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                      ('^login/$',login),
                      ('^test/$',test),
    # Examples:
    # url(r'^$', 'weibo_test.views.home', name='home'),
    # url(r'^weibo_test/', include('weibo_test.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
