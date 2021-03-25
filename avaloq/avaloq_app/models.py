from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid
import datetime


# Number of days that the URL will be active for candidates to use
EXPIRY_TIME = 7


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_reviewer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


class CodeTemplate(models.Model):
    name = models.TextField(null=False)
    language = models.TextField(null=False)
    template = models.TextField(null=False)

    def __str__(self):
        return self.name

    def add_template(self, data):
        self.language = data['language']
        self.template = data['template']
        self.name = data['name']
        self.save()


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Question(models.Model):
    title = models.TextField()
    text = models.TextField()
    q_id = models.IntegerField(default=0, primary_key=True)
    time = models.IntegerField(null=True)
    templates = models.ManyToManyField(CodeTemplate)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    forename = models.TextField()
    surname = models.TextField()
    unique_id = models.TextField()
    questions = models.ManyToManyField(Question)
    q1_sub = models.BooleanField(default=False)
    q2_sub = models.BooleanField(default=False)
    init_time = models.DateTimeField(default=None, null=True)
    q1_start = models.DateTimeField(default=None, null=True, blank=True)
    q2_start = models.DateTimeField(default=None, null=True, blank=True)
    q1_exp = models.DateTimeField(default=None, null=True, blank=True)
    q2_exp = models.DateTimeField(default=None, null=True, blank=True)
    q1_end = models.DateTimeField(default=None, null=True, blank=True)
    q2_end = models.DateTimeField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):

        self.init_time = datetime.datetime.now()
        if self.unique_id == "":
            self.unique_id = str(uuid.uuid4())
            self.init_time = datetime.datetime.now()

        super(Candidate, self).save(*args, **kwargs)

    def __str__(self):
        return self.forename

    def add_code(self, data):
        ce = Code_Entry()

        if data['is_submitted'] and (data['q_num'] == 0):

            self.q1_sub = True
            ce.final = True
            self.q1_end = datetime.datetime.now()

        elif data['is_submitted'] and (data['q_num'] == 1):

            self.q2_sub = True
            ce.final = True
            self.q2_end = datetime.datetime.now()

        ce.unique_id = data['uid']
        ce.code = data['code']

        ce.language = data['language']

        if 'verdicts' in data:
            ce.verdicts = data['verdicts']

        ce.candidate = self
        ce.question = self.questions.all()[data['q_num']]

        ce.save()
        self.save()

    def set_start(self, q_num):

        if (q_num == 0):
            self.q1_start = datetime.datetime.now()
        else:
            self.q2_start = datetime.datetime.now()

        self.save()

    def get_start(self, q_num):

        if (q_num == 0):
            return self.q1_start

        else:
            return self.q2_start

    def get_exp(self, q_num):

        if (q_num == 0):

            if not self.q1_exp:

                self.q1_exp = self.q1_start + \
                    datetime.timedelta(
                        minutes=self.questions.values('time')[0]['time'])

            return (self.q1_exp)

        else:

            if not self.q2_exp:

                self.q2_exp = self.q2_start + \
                    datetime.timedelta(
                        minutes=self.questions.values('time')[1]['time'])
            return (self.q2_exp)

    def get_sub(self, q_num):

        if q_num == 0:

            return self.q1_sub

        else:

            return self.q2_sub

    def is_submitted(self):
        return self.q1_sub and self.q2_sub

    def is_expired(self):
        days_old = (datetime.datetime.now() - self.init_time).days

        if(days_old > EXPIRY_TIME):
            return True
        else:
            return False

    def has_started(self):
        if(self.q1_start is None and self.q2_start is None):
            return False
        else:
            return True


class Code_Entry(models.Model):

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    final = models.BooleanField(default=False)
    code = models.TextField(null=True)
    language = models.TextField(null=True)
    verdicts = models.TextField(null=True)

    def __str__(self):
        return self.code
