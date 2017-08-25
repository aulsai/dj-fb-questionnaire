from django.conf.urls import patterns, include, url

from app_fb_questionnaire.views import *

urlpatterns = patterns('',
    
    url(r'qs/compare/(?P<friend_id>[0-9]+)/(?P<question_set_id>[0-9]+)/',\
            QuestionnaireCompareTemplateView.as_view(), name='questionnaire-compare'),    
    url(r'qs/save', questionnaire_save, name='questionnaire-save'),
    url(r'qs/share/(?P<fb_user_id>[0-9]+)/(?P<question_set_id>[0-9]+)/new/',\
            QuestionnaireListView.as_view(), name='questionnaire-friend'),    
    url(r'qs/share/(?P<fb_user_id>[0-9]+)/(?P<question_set_id>[0-9]+)/',\
            QuestionnaireShareTemplateView.as_view(), name='questionnaire-share'),
    url(r'qs/(?P<question_set_id>[0-9]+)', QuestionnaireListView.as_view(), name='questionnaire'),
    url(r'^', HomeView.as_view(), name='home'),
)
