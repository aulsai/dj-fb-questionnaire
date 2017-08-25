from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'proj_fb_questionnaire.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),   
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')), 
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('app_fb_questionnaire.urls')),
)
