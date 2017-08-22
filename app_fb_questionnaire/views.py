import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from app_fb_questionnaire.models import *


class HomeView(ListView):

    model = QuestionSet
    template_name = 'app_fb_questionnaire/home.html'


class QuestionnaireShareTemplateView(TemplateView):

    template_name = 'app_fb_questionnaire/share.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireShareTemplateView, self).get_context_data(**kwargs)
        fb_user_id = kwargs.get('fb_user_id')
        question_set_id = kwargs.get('question_set_id')
        
        return context

class QuestionnaireListView(TemplateView):

    template_name = 'app_fb_questionnaire/questionnaire.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireListView, self).get_context_data(**kwargs)

        question_set_id = kwargs.get('pk')
        context['question_set_id'] = question_set_id
        
        qs = QuestionSet.objects.filter(id=question_set_id)\
            .values(
            'questionsetitem',
            'questionsetitem__question_variation_id__questionchoice__question_id',
            'questionsetitem__question_variation_id__questionchoice__question_id__text',
            'questionsetitem__question_variation_id__questionchoice',
            'questionsetitem__question_variation_id__questionchoice__choice_id__text'
        )
        context['qs'] = self._transform_data(qs)
        context['questionnaire'] = [
            {
                'question': "Q1",
                'question_set_item_id': 1,
                'choices': [
                    {
                        'question_choice_id': 1,
                        'question_choice_name': 'BMW'
                    },
                    {
                        'question_choice_id': 2,
                        'question_choice_name': 'Audi'
                    }
                ]
            },
            {
                'question': "Q2",
                'question_set_item_id': 2,
                'choices': [
                    {
                        'question_choice_id': 3,
                        'question_choice_name': 'Red'
                    },
                    {
                        'question_choice_id': 4,
                        'question_choice_name': 'Blue'
                    }
                ]
            }
        ]

        return context

    def _transform_data(self, qs):
        map = {}
        for q in qs:
            qi_id = q['questionsetitem']
            q_id = q['questionsetitem__question_variation_id__questionchoice__question_id']
            q_text = q['questionsetitem__question_variation_id__questionchoice__question_id__text']
            c_id = q['questionsetitem__question_variation_id__questionchoice']
            c_text = q['questionsetitem__question_variation_id__questionchoice__choice_id__text']

            if q_id in map:
                map[q_id]['choices'].append({
                    'question_choice_id': c_id,
                    'question_choice_name': c_text
                })
            else:
                map[q_id] = {
                    'question': q_text,
                    'question_set_item_id': qi_id,
                    'choices': [
                        {
                            'question_choice_id': c_id,
                            'question_choice_name': c_text
                        }
                    ]
                }

        return map.viewvalues()

def questionnaire_save(request):

    if request.method == 'POST':
        # Grep Values from form
        form_values = _grep_body_data(request.body)
        question_set_id = form_values.get('question_set_id')
        fb_user_id = form_values.get('fb_user_id')
        fb_user_name = form_values.get('fb_user_name')

        list_answer = [form_values[f]
                       for f in form_values if f.startswith('choice_')]

        # Create User
        # id
        # name
        user = _create_user(fb_user_id, fb_user_name)

        # Create QuestionSetUser
        # question_set_id
        # user_id
        question_set_user = _create_question_set_user(user, question_set_id)

        # Create Answer
        _create_question_set_user_answer(question_set_user, list_answer)

        # TODO - Redirect to share page
        
        return redirect(reverse('questionnaire-share', args=[user.ext_id, question_set_id]))

    return redirect('/')


def _grep_body_data(body):
    form_values = {}
    for field in body.split('&'):
        key, value = field.split('=')
        form_values[key] = value

    return form_values


def _create_user(fb_user_id, fb_user_name):
    try:
        return FBUser.objects.get(ext_id=fb_user_id)
    except FBUser.DoesNotExist:
        return FBUser.objects.create(
            ext_id=fb_user_id,
            name=fb_user_name
        )


def _create_question_set_user(user, question_set_id):

    try:
        qsu = QuestionSetUser.objects.order_by('-id').filter(fb_user_id=user, question_set_id=question_set_id).first()        
        if qsu is None:
            raise QuestionSetUser.DoesNotExist
        return qsu
    except QuestionSetUser.DoesNotExist:

        qs = QuestionSet.objects.get(pk=question_set_id)

        return QuestionSetUser.objects.create(
            fb_user_id=user,
            question_set_id=qs
        )


def _create_question_set_user_answer(question_set_user, list_answer):
    # TODO - Bulk create
    for ans in list_answer:
        #key, question_choice_id = ans.split('=')

        qc = QuestionChoice.objects.get(pk=ans)

        QuestionSetUserAnswer.objects.create(
            question_set_user_id=question_set_user,
            question_choice_id=qc
        )
