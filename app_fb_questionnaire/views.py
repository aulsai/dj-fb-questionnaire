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
        
        context['share_link'] = "example.com/ref/{0}/qs/{1}/".format(fb_user_id, question_set_id)
        return context

class QuestionnaireCompareTemplateView(TemplateView):

    template_name = 'app_fb_questionnaire/result_compare.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireCompareTemplateView, self).get_context_data(**kwargs)
        friend_id = kwargs.get('friend_id')
        question_set_id = kwargs.get('question_set_id')

        # Get Friend object
        friend = Friend.objects.filter(pk=friend_id).first()

        # Get Latest QuestionSetUser
        qsu_ref = QuestionSetUser.objects\
                    .order_by('-id')\
                    .filter(question_set_id__id=question_set_id, fb_user_id=friend.referrer)\
                    .first()
                    
        qsu_user = QuestionSetUser.objects\
                    .order_by('-id')\
                    .filter(question_set_id__id=question_set_id, fb_user_id=friend.user)\
                    .first()

        #qsi_ref = QuestionSetItem.objects.all().filter(question_set_id=qsu_ref.question_set_id)
        #qsi_user = QuestionSetItem.objects.all().filter(question_set_id=qsu_user.question_set_id)
        from django.db.models import Count
        user_and_friend_answer_same_choice = QuestionSetUserAnswer.objects.all()\
                                    .filter(question_set_user_id__in=[qsu_ref, qsu_user])\
                                    .values('question_choice_id')\
                                    .annotate(count_ans=Count('question_choice_id'))\
                                    .filter(count_ans__gt=1)
        
        context['res'] = user_and_friend_answer_same_choice
        return context

class QuestionnaireListView(TemplateView):

    template_name = 'app_fb_questionnaire/questionnaire.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireListView, self).get_context_data(**kwargs)

        question_set_id = kwargs.get('question_set_id')
        # When fb_user_id is provided, friend will be create
        fb_user_id = kwargs.get('fb_user_id')
        
        context['fb_user_id'] = fb_user_id
        context['question_set_id'] = question_set_id
        
        # TODO - Move to model's query set
        qs = QuestionSet.objects.filter(id=question_set_id)\
            .values(
            'questionsetitem',
            'questionsetitem__question_variation_id__questionchoice__question_id',
            'questionsetitem__question_variation_id__questionchoice__question_id__text',
            'questionsetitem__question_variation_id__questionchoice',
            'questionsetitem__question_variation_id__questionchoice__choice_id__text'
        )
        context['qs'] = self._transform_data(qs)        

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

        ref_fb_user_id = form_values.get('ref_fb_user_id')

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

        #_create_friend
        friend = _create_friend(user, ref_fb_user_id)    
        if friend:
            return redirect(reverse('questionnaire-compare', args=[friend.id, question_set_id]))

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

    qs = QuestionSet.objects.get(pk=question_set_id)

    return QuestionSetUser.objects.create(
        fb_user_id=user,
        question_set_id=qs
    )

    """
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
    """

def _create_question_set_user_answer(question_set_user, list_answer):
    # TODO - Bulk create
    for ans in list_answer:
        #key, question_choice_id = ans.split('=')

        qc = QuestionChoice.objects.get(pk=ans)

        QuestionSetUserAnswer.objects.create(
            question_set_user_id=question_set_user,
            question_choice_id=qc
        )

def _create_friend(user, ref_fb_user_id):

    try:
        existing_relation = Friend.objects.filter(referrer__ext_id=ref_fb_user_id, user=user).first()
        if not existing_relation:
            raise Friend.DoesNotExist
    
        return existing_relation

    except Friend.DoesNotExist:        
        ref = None
        try:
            ref = FBUser.objects.get(ext_id=ref_fb_user_id)
        except FBUser.DoesNotExist:
            return None
        
        return Friend.objects.create(
            referrer=ref,
            user=user
        )