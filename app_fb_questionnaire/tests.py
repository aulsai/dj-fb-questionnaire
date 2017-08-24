# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.db.models import Count

from .models import *


class QuestionModelTests(TestCase):
    
    def setUp(self):
        self.q1 = Question.objects.create(
            text='What is your favorite car?'
        )
        self.q2 = Question.objects.create(
            text='What is your current car?'
        )

    def test_create_question(self):
        q1 = Question.objects.filter(text='What is your favorite car?').first()                
        self.assertEqual(self.q1, q1)
        
    def test_count_question(self): 
        count = Question.objects.count()
        self.assertEqual(2, count)   

class ChoiceModelTests(TestCase):

    def setUp(self):
        self.c1 = Choice.objects.create(
            text='BMW'
        )
        self.c2 = Choice.objects.create(
            text='Audi'
        )

    def test_create_choice(self):
        c1 = Choice.objects.filter(text='BMW').first()        
        self.assertEqual(self.c1, c1)
            
    def test_count_choice(self):
        count = Choice.objects.count()
        self.assertEqual(2, count)


class QuestionVariationModelTests(TestCase):

    def setUp(self):

        self.qv1 = QuestionVariation.objects.create(
            name='Favorite car 1'
        )

        self.qv2 = QuestionVariation.objects.create(
            name='Favorite car 2'
        )

        self.q1 = Question.objects.create(
            text='What is your favorite car?'
        )

        self.c1 = Choice.objects.create(
            text='BMW'
        )
        self.c2 = Choice.objects.create(
            text='Audi'
        )

        self.c3 = Choice.objects.create(
            text='Ford'
        )

        self.c4 = Choice.objects.create(
            text='Tesla'
        )

        self.qc1 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c1,
        )

        self.qc2 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c2,
        )

        self.qc3 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c3,
        )

        self.qc4 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c4,
        )
    
    def test_question_variation_one(self):

        qv1 = QuestionVariation.objects.filter(name=self.qv1.name).first()
        qc = qv1.questionchoice_set.order_by('id').all()

        qc_count = QuestionVariation.objects.values('questionchoice').filter(name=self.qv1.name).count()
        
        self.assertEqual(2, qc_count)
        self.assertEqual(self.qc1, qc[0])
        self.assertEqual(self.qc2, qc[1])

    def test_question_variation_two(self):

        qv2 = QuestionVariation.objects.filter(name=self.qv2.name).first()
        qc = qv2.questionchoice_set.order_by('id').all()

        qc_count = QuestionVariation.objects.values('questionchoice').filter(name=self.qv2.name).count()
        
        self.assertEqual(2, qc_count)
        self.assertEqual(self.qc3, qc[0])
        self.assertEqual(self.qc4, qc[1])


class QuestioinSetModelTests(TestCase):
    
    def _setUpQuestionVariationModelTests(self):

        self.qv1 = QuestionVariation.objects.create(
            name='Favorite car 1'
        )

        self.qv2 = QuestionVariation.objects.create(
            name='Favorite car 2'
        )

        self.q1 = Question.objects.create(
            text='What is your favorite car?'
        )

        self.c1 = Choice.objects.create(
            text='BMW'
        )
        self.c2 = Choice.objects.create(
            text='Audi'
        )

        self.c3 = Choice.objects.create(
            text='Ford'
        )

        self.c4 = Choice.objects.create(
            text='Tesla'
        )

        self.qc1 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c1,
        )

        self.qc2 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c2,
        )

        self.qc3 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c3,
        )

        self.qc4 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c4,
        )

    def setUp(self):

        self._setUpQuestionVariationModelTests()

        self.qs1 = QuestionSet.objects.create(
            name='Question Set A'
        )

        self.qs2 = QuestionSet.objects.create(
            name='Question Set B'
        )

        self.qsItem1 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv1
        )

        self.qsItem2 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv2
        )
    
    def test_question_set_count(self):

        qs1 = QuestionSet.objects.filter(name=self.qs1.name).first()
        qs2 = QuestionSet.objects.filter(name=self.qs2.name).first()

        count_qs1 = qs1.questionsetitem_set.all().count()
        count_qs2 = qs2.questionsetitem_set.all().count()

        self.assertEqual(2, count_qs1)
        self.assertEqual(0, count_qs2)

    def test_get_question_choice_list_to_render(self):
        question_choice_list = QuestionSet.objects.get_question_and_choice_list_by_question_set_id(self.qs1.pk)

        self.assertEqual(1, len(question_choice_list))
        

class FBUserModelTests(TestCase):

    def setUp(self):

        self.user1 = FBUser.objects.create(
            ext_id=11111,
            name='FB User 1'
        )

        self.user2 = FBUser.objects.create(
            ext_id=22222,
            name='FB User 2'
        )

    def test_fb_user_count(self):

        count_user = FBUser.objects.all().count()

        self.assertEqual(2, count_user)


class QuestionSetUserModelTests(TestCase):

    def _setUpQuestionVariationModelTests(self):

        self.qv1 = QuestionVariation.objects.create(
            name='Favorite car 1'
        )

        self.qv2 = QuestionVariation.objects.create(
            name='Favorite car 2'
        )

        self.q1 = Question.objects.create(
            text='What is your favorite car?'
        )

        self.c1 = Choice.objects.create(
            text='BMW'
        )
        self.c2 = Choice.objects.create(
            text='Audi'
        )

        self.c3 = Choice.objects.create(
            text='Ford'
        )

        self.c4 = Choice.objects.create(
            text='Tesla'
        )

        self.qc1 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c1,
        )

        self.qc2 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c2,
        )

        self.qc3 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c3,
        )

        self.qc4 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c4,
        )

    def _setUpQuestioinSetModelTests(self):
        
        self.qs1 = QuestionSet.objects.create(
            name='Question Set A'
        )

        self.qs2 = QuestionSet.objects.create(
            name='Question Set B'
        )

        self.qsItem1 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv1
        )

        self.qsItem2 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv2
        )

    def _setUpFBUserModelTests(self):                

        self.user1 = FBUser.objects.create(
            ext_id=11111,
            name='FB User 1'
        )

        self.user2 = FBUser.objects.create(
            ext_id=22222,
            name='FB User 2'
        )

    def setUp(self):
        self._setUpQuestionVariationModelTests()
        self._setUpQuestioinSetModelTests()
        self._setUpFBUserModelTests()

        self.qsu1 = QuestionSetUser.objects.create(
            question_set_id=self.qs1,
            fb_user_id=self.user1
        )        

        self.qsu2 = QuestionSetUser.objects.create(
            question_set_id=self.qs1,
            fb_user_id=self.user2
        )

    def test_question_set_user_count(self):

        qsu1 = QuestionSetUser.objects.filter(fb_user_id=self.user1).count()
        qsu2 = QuestionSetUser.objects.filter(fb_user_id=self.user2).count()

        self.assertEqual(1, qsu1)
        self.assertEqual(1, qsu2)


class QuestionSetUserAnswerModelTests(TestCase):

    def _setUpQuestionVariationModelTests(self):

        self.qv1 = QuestionVariation.objects.create(
            name='Favorite car 1'
        )

        self.qv2 = QuestionVariation.objects.create(
            name='Favorite car 2'
        )

        self.q1 = Question.objects.create(
            text='What is your favorite car?'
        )

        self.c1 = Choice.objects.create(
            text='BMW'
        )
        self.c2 = Choice.objects.create(
            text='Audi'
        )

        self.c3 = Choice.objects.create(
            text='Ford'
        )

        self.c4 = Choice.objects.create(
            text='Tesla'
        )

        self.qc1 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c1,
        )

        self.qc2 = QuestionChoice.objects.create(
            question_variation_id=self.qv1,
            question_id=self.q1,
            choice_id=self.c2,
        )

        self.qc3 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c3,
        )

        self.qc4 = QuestionChoice.objects.create(
            question_variation_id=self.qv2,
            question_id=self.q1,
            choice_id=self.c4,
        )

    def _setUpQuestioinSetModelTests(self):
        
        self.qs1 = QuestionSet.objects.create(
            name='Question Set A'
        )

        self.qs2 = QuestionSet.objects.create(
            name='Question Set B'
        )

        self.qsItem1 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv1
        )

        self.qsItem2 = QuestionSetItem.objects.create(
            question_set_id=self.qs1,
            question_variation_id=self.qv2
        )

    def _setUpFBUserModelTests(self):                

        self.user1 = FBUser.objects.create(
            ext_id=11111,
            name='FB User 1'
        )

        self.user2 = FBUser.objects.create(
            ext_id=22222,
            name='FB User 2'
        )

    def _setUpQuestionSetUserModelTests(self):
        
        self.qsu1 = QuestionSetUser.objects.create(
            question_set_id=self.qs1,
            fb_user_id=self.user1
        )        

        self.qsu2 = QuestionSetUser.objects.create(
            question_set_id=self.qs1,
            fb_user_id=self.user2
        )

    def setUp(self):

        self._setUpQuestionVariationModelTests()
        self._setUpQuestioinSetModelTests()
        self._setUpFBUserModelTests()
        self._setUpQuestionSetUserModelTests()
        
        self.qsua_user_1_question_1 = QuestionSetUserAnswer.objects.create(
            question_set_user_id=self.qsu1,
            question_choice_id=self.qc1
        )

        self.qsua_user_1_question_2 = QuestionSetUserAnswer.objects.create(
            question_set_user_id=self.qsu1,
            question_choice_id=self.qc3
        )

        self.qsua_user_2_question_1 = QuestionSetUserAnswer.objects.create(
            question_set_user_id=self.qsu2,
            question_choice_id=self.qc1
        )

        self.qsua_user_2_question_2 = QuestionSetUserAnswer.objects.create(
            question_set_user_id=self.qsu2,
            question_choice_id=self.qc4
        )

    def test_question_set_user_answer_count(self):

        qsua_user_1 = QuestionSetUserAnswer.objects.filter(question_set_user_id=self.qsu1).count()
        qsua_user_2 = QuestionSetUserAnswer.objects.filter(question_set_user_id=self.qsu2).count()

        self.assertEqual(2, qsua_user_1)
        self.assertEqual(2, qsua_user_2)
    
    def test_two_user_answer_on_the_same_choices(self):        

        user_and_friend_answer_same_choice = QuestionSetUserAnswer.objects\
                                                .get_same_answer_by_two_question_set_user(self.qsu1, self.qsu2)

        user_and_friend_answer_same_choice_rate = QuestionSetUserAnswer.objects\
                                                .get_same_answer_rate_by_two_question_set_user(self.qsu1, self.qsu2)
                                   
        self.assertEqual(1, len(user_and_friend_answer_same_choice))
        self.assertEqual(self.qc1.id, user_and_friend_answer_same_choice[0]['question_choice_id'])
        self.assertEqual(50, user_and_friend_answer_same_choice_rate)
