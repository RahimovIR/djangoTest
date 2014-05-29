from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from tables.api import my_resource

admin.autodiscover()

tables_api = Api(api_name='tables')
for resource in my_resource:
    tables_api.register(resource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tables.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(tables_api.urls)),
)
