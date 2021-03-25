import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avaloq.settings')
import django
django.setup()
import json
import string
import datetime
import random
from avaloq_app.models import *
from django.contrib.auth.models import User


def snippets():
    snippets = ['aaaa ']
    for i in range(10):
        p = snippets[i]
        snippets.append(p + ''.join(random.choice(string.ascii_letters)
                        for _ in range(4)) + ' ')
    return snippets


def get_snippet(code, submitted, q, lang, c, verdicts=None):
    if verdicts is None:
        return {"code": code,
                "is_submitted": submitted,
                "q_num": q,
                'language': lang,
                'uid': c,
                }
    else:
        return {"code": code,
                "is_submitted": submitted,
                "q_num": q,
                'language': lang,
                'uid': c,
                "verdicts": json.dumps(verdicts)}


def populate():
    # this should read questions from files and populate question objects when we have a question directory
    questions = [{'q_id': 1, 'time': 600, 'title': "Triangle Quest",
                  'text': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."},
                 {'q_id': 2, 'time': 600, 'title': "Roman Numbers",
                  'text': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."},
                 {'q_id': 3, 'time': 600, 'title': "Reverse Array",
                  'text': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."},
                 {'q_id': 4, 'time': 600, 'title': "Duplicate Num",
                  'text': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."},
                 {'q_id': 5, 'time': 600, 'title': "Palindrome",
                  'text': "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."}]

    firstnames = ['Liam', 'Emma', 'Oliver', 'Anna',
                  'James', 'Ben', 'Sam', 'Simon', 'David']
    surnames = ['Smith', 'Johnson', 'Williams', 'Brown',
                'Jones', 'Miller', 'Davis', 'White', 'Martin']

    for question in questions:
        q = Question.objects.get_or_create(time=question['time'], q_id=question['q_id'], title=question['title'],
                                           text=question['text'])[0]
        # q.time = question['time']
        # q.title=question['title']
        # q.text=question['text']
        q.save()

    for f, s in zip(firstnames, surnames):
        queryset = Question.objects.all().order_by('q_id')[:2]
        q1 = queryset[0]
        q2 = queryset[1]
        time_init = datetime.datetime.now()
        c = Candidate.objects.get_or_create(
            forename=f, surname=s, init_time=time_init, unique_id=str(uuid.uuid4()))[0]

        c.questions.add(q1)
        c.questions.add(q2)
        c.save()

    users = [{'username': 'admin', 'password': 'admin', 'is_admin': True},
             {'username': 'reviewer', 'password': 'reviewer', 'is_admin': False}]

    for user in users:
        username = user['username']
        password = user['password']
        admin = user['is_admin']

        u = User.objects.create_user(username=username, password=password)
        u.is_superuser = admin
        u.is_staff = admin
        u.save()

        up = Profile.objects.get_or_create(user=u)[0]

        up.is_admin = admin
        up.save()

    # submitted_candidates = Candidate.objects.all().order_by('?')[:2]

    # for c in submitted_candidates:
    #     data1 = {'is_submitted': False, 'uid': c.unique_id, 'code': "Hello wo..", 'language': 'Python', 'q_num': 1}
    #     data2 = {'is_submitted': True, 'uid': c.unique_id, 'code': 'Hello world, this is finished now','language': 'Python', 'q_num': 1}

        # c.add_code(data1)
        # c.add_code(data2)
        # c.q1_sub = True
        # c.q2_sub = True
        # c.save()

    # language templates

    t1 = CodeTemplate()
    t1.add_template({'language': 'python',
                     'template': "\\n",
                     'name': 'defaultpy'})
    t1.save()
    t2 = CodeTemplate()
    t2.add_template({'language': 'java',
                     'template': "public class Main {\\n\\tpublic static void main(String[] args) {\\n\\t}\\n}",
                     'name': 'defaultjava'})
    t2.save()

    for c in Candidate.objects.all():
        snips = snippets()
        for q in range(2):
            for s in snips:

                c.add_code(get_snippet(s, False, q, 'python', c))
            # c.add_code(get_snippet(snips[-1] + " END", True, q, 'python', c, verdicts={'sample1': 'OK', 'sample2': 'OK'}))


if __name__ == '__main__':
    print('Starting population script...')
    populate()
