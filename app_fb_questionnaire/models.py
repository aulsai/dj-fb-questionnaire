from django.db import models


class Question(models.Model):

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


class QuestionSetUser(models.Model):
    question_set_id = models.ForeignKey(QuestionSet)
    fb_user_id = models.ForeignKey(FBUser)

    def __str__(self):
        return "{0}_{1}".format(self.question_set_id.name, self.fb_user_id.name)


class QuestionSetUserAnswer(models.Model):

    question_set_user_id = models.ForeignKey(QuestionSetUser)
    question_choice_id = models.ForeignKey(QuestionChoice)

    def __str__(self):
        return "User {0} has answered in Question Set: {1} this choice: {2}".format(self.question_set_user_id.fb_user_id, \
                                self.question_set_user_id.question_set_id,\
                                self.question_choice_id)
