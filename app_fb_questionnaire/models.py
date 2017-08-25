from django.db import models
from django.db.models import Count


class Question(models.Model):
    """
    To store each question
    """
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Choice(models.Model):

    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class QuestionVariation(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class QuestionChoice(models.Model):

    question_id = models.ForeignKey(Question)
    choice_id = models.ForeignKey(Choice)
    question_variation_id = models.ForeignKey(QuestionVariation, null=True, blank=True)

    def __str__(self):
        return self.question_id.text + '_' + self.choice_id.text


class FBUser(models.Model):

    ext_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.ext_id + "_" + self.name


class Friend(models.Model):
    referrer = models.ForeignKey('FBUser', related_name='referrer')
    user = models.ForeignKey('FBUser')

    class Meta:
        unique_together = ('referrer', 'user')

    def __str__(self):
        return self.referrer.name + "_" + self.user.name

class QuestionSetManager(models.Manager):

    def list_question_choices(self, question_set_id):
        return self.filter(id=question_set_id)\
            .values(
                'questionsetitem',
                'questionsetitem__question_variation_id__questionchoice__question_id',
                'questionsetitem__question_variation_id__questionchoice__question_id__text',
                'questionsetitem__question_variation_id__questionchoice',
                'questionsetitem__question_variation_id__questionchoice__choice_id__text'
            )

    def get_question_and_choice_list_by_question_set_id(self, question_set_id):
        qs = self.list_question_choices(question_set_id)
        dict_display = {}
        for q in qs:
            qi_id = q['questionsetitem']
            q_id = q['questionsetitem__question_variation_id__questionchoice__question_id']
            q_text = q['questionsetitem__question_variation_id__questionchoice__question_id__text']
            c_id = q['questionsetitem__question_variation_id__questionchoice']
            c_text = q['questionsetitem__question_variation_id__questionchoice__choice_id__text']

            if q_id in dict_display:
                dict_display[q_id]['choices'].append({
                    'question_choice_id': c_id,
                    'question_choice_name': c_text
                })
            else:
                dict_display[q_id] = {
                    'question': q_text,
                    'question_set_item_id': qi_id,
                    'choices': [
                        {
                            'question_choice_id': c_id,
                            'question_choice_name': c_text
                        }
                    ]
                }

        return dict_display.viewvalues()


class QuestionSet(models.Model):

    name = models.CharField(max_length=255)  

    objects = QuestionSetManager()

    def __str__(self):
        return self.name


class QuestionSetItem(models.Model):

    question_set_id = models.ForeignKey(QuestionSet)
    question_variation_id = models.ForeignKey(QuestionVariation)

    def __str__(self):
        return self.question_set_id.name + "_" + self.question_variation_id.name


class QuestionSetUserManager(models.Manager):

    def get_latest_by_id_and_user_id(self, question_set_id, fb_user_id):
        return self.order_by('-id')\
                        .filter(question_set_id__id=question_set_id, fb_user_id__ext_id=fb_user_id)\
                        .first()

class QuestionSetUser(models.Model):
    question_set_id = models.ForeignKey(QuestionSet)
    fb_user_id = models.ForeignKey(FBUser)

    objects = QuestionSetUserManager()

    def __str__(self):
        return "{0}_{1}".format(self.question_set_id.name, self.fb_user_id.name)


class QuestionSetUserAnswerManager(models.Manager):

    def get_all_choices_by_question_set_user(self, qsu_ref, qsu_user):
        return self.all()\
                .filter(question_set_user_id__in=[qsu_ref, qsu_user])\
                .values('question_choice_id')                               


    def count_total_choices_by_question_set_user(self, qsu_ref, qsu_user):
        # Devide by two because it would get for 2 people.
        return self.get_all_choices_by_question_set_user(qsu_ref, qsu_user).count() / 2

    def get_same_answer_by_two_question_set_user(self, qsu_ref, qsu_user):
        return self.get_all_choices_by_question_set_user(qsu_ref, qsu_user)\
                    .annotate(count_ans=Count('question_choice_id'))\
                    .filter(count_ans__gt=1)

    def count_same_answer_by_two_question_set_user(self, qsu_ref, qsu_user):
        return self.get_same_answer_by_two_question_set_user(qsu_ref, qsu_user)\
                    .count()
    
    def get_same_answer_rate_by_two_question_set_user(self, qsu_ref, qsu_user):
        count_same_answer = self.count_same_answer_by_two_question_set_user(qsu_ref, qsu_user)
        count_total_choices = self.count_total_choices_by_question_set_user(qsu_ref, qsu_user)
        return (count_same_answer * 100) / float(count_total_choices)




class QuestionSetUserAnswer(models.Model):

    question_set_user_id = models.ForeignKey(QuestionSetUser)
    question_choice_id = models.ForeignKey(QuestionChoice)

    objects = QuestionSetUserAnswerManager()

    def __str__(self):
        return "User {0} has answered in Question Set: {1} this choice: {2}".format(self.question_set_user_id.fb_user_id, \
                                self.question_set_user_id.question_set_id,\
                                self.question_choice_id)
