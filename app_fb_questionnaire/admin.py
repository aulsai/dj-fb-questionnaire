from django.contrib import admin

from app_fb_questionnaire.models import *


admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuestionVariation)
admin.site.register(QuestionChoice)
admin.site.register(QuestionSet)
admin.site.register(QuestionSetItem)
admin.site.register(FBUser)
admin.site.register(Friend)
admin.site.register(QuestionSetUser)
admin.site.register(QuestionSetUserAnswer)


