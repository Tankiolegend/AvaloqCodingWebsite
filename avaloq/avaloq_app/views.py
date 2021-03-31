import os
from pathlib import Path
import time
import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import RequestContext

from sys import platform

from avaloq_app.testutil import get_all_tests, get_sample_tests, get_inputs

if platform == "linux" or platform == "linux2":
    from avaloq_app.testsystem import TestSystem, LANGS  # get_output, get_verdicts
else:
    from avaloq_app.fakesystem import TestSystem, LANGS  # get_output, get_verdicts

from django.http import HttpResponse, JsonResponse
from django.views import View
from avaloq_app.models import Candidate, CodeTemplate, Code_Entry
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CodeForm, CandidateForm, CreateStaff

import json
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")
test_case_path = config['PATHS']['test_cases']

question_folder = os.path.join(
    Path(__file__).resolve().parent.parent, 'tasks/questions')

test_system = TestSystem()


def expired(request):
    return render(request, 'avaloq_app/expired.html')


def completion(request):
    context_dict = {}
    return render(request, 'avaloq_app/completion.html', context=context_dict)

def page_not_found(request,exception):
    response = render(request=request,template_name='web_errors/404.html')
    response.status_code = 404
    return response

def bad_request(request,exception):
    response = render(request=request,template_name='web_errors/400.html')
    response.status_code = 400
    return response

def server_error(request):
    response = render(request=request,template_name='web_errors/500.html')
    response.status_code = 500
    return response

def permission_denied(request,exception):
    response = render(request=request,template_name='web_errors/403.html')
    response.status_code = 403
    return response



def home(request, u_id):
    context_dict = {}

    try:
        candidate = Candidate.objects.get(unique_id=u_id)
        context_dict['candidate'] = candidate
        context_dict['questions'] = candidate.questions.all()

        context_dict['q1_submitted'] = candidate.q1_sub
        context_dict['q2_submitted'] = candidate.q2_sub

        if(candidate.is_submitted()):
            return redirect(reverse('avaloq:completion'))

        if(candidate.is_expired()):
            return redirect(reverse('avaloq:expired'))

        counter = 0
        for q in context_dict['questions']:
            q.num = counter
            counter += 1

    except Candidate.DoesNotExist:

        return HttpResponse("uh")
    return render(request, 'avaloq_app/home.html', context=context_dict)


# convert isolate messages
def _get_compiler_message(code):
    if code == 'WA':
        return 'Wrong Answer'
    elif code == 'TO':
        return 'Timed Out'
    elif code == 'RE':
        return 'Run-Time Error'
    elif code == 'CE':
        return 'Compilation Error'
    elif code == 'SG':
        return 'Program died on a signal'
    elif code == 'XX':
        return 'internal Error '
    else:  # if code == 'OK':
        return 'Compilation Successful'

def get_code(request, u_id, q_num):
    context_dict = {}
    int_q_num = int(q_num)
    try:
        candidate = Candidate.objects.get(unique_id=u_id)
        context_dict['candidate'] = candidate
        context_dict['q_num'] = int(q_num)
        context_dict['q'] = candidate.questions.all()[int(q_num)]

    except Candidate.DoesNotExist:

        return HttpResponse("CandidateNotFound")

    start = candidate.get_start(int_q_num)

    if start is None:
        candidate.set_start(int_q_num)

    context_dict['exp_time'] = int(time.mktime(
        candidate.get_exp(int_q_num).timetuple())) * 1000

    # ----- get question path -----
    question_text = candidate.questions.values('text')[int_q_num]['text']  
    if (question_text.endswith('.md') and (len(question_text) < 50)):

        path = os.path.join(question_folder, question_text)

        if os.path.exists(path):
            with open(path, 'r') as file:
                question_text = file.read()

    context_dict['question'] = question_text

    # ----- get templates for languages -----
    code_templates = CodeTemplate.objects.all()
    templates = {}
    for t in code_templates:
        templates[t.language] = t.template
    context_dict["templates"] = json.dumps(templates)

    if request.method == 'POST' or request.is_ajax:

        form = CodeForm(request.POST)
        if form.is_valid():
            code_input = form.cleaned_data['code_text']
            test_case = form.cleaned_data['test_input']
            lang = form.cleaned_data['language']  # for future use
        testing_folder = os.path.join(
            'tasks/test_cases/', str(candidate.questions.all()[int(q_num)].q_id))

        redirect_url = reverse('avaloq:home', kwargs={'u_id': u_id})

        if request.is_ajax():
            # initial back end timer check, if the time has expired return a response to js file to do a redirect
            if candidate.get_exp(int_q_num) < datetime.datetime.now():

                if lang is not None:
                    verdicts = test_system.get_verdicts(
                        LANGS[lang], code_input, get_all_tests(testing_folder))
                else:
                    verdicts = ""
                candidate.add_code({"code": code_input, "is_submitted": True,
                                    'language': lang, 'uid': candidate.unique_id, 'q_num': int_q_num,
                                    "verdicts": json.dumps(verdicts)})

                # Since using ajax can not redirect using python must return a response and have the js perform redirection
                # Compromise made to prevent page refresh
                response = {'redirect': True,
                            'redirect_url': redirect_url,
                            }
                return JsonResponse(response)

            if request.method == 'GET':

                response = {'redirect': False,
                            'exp_time': context_dict['exp_time'],
                            }
                return JsonResponse(response)

            # running code against user's input or sample inputs
            elif 'user_test_input' in request.POST:

                form = CodeForm(request.POST)

                if form.is_valid():
                    user_test_input = form.cleaned_data['user_test_input']

                    # if it brakes use: request.POST.get('user_test_input')
                    if not user_test_input:
                        results = test_system.get_outputs(LANGS[lang], code_input, testing_folder=testing_folder)  # get_output(code_input, test_case)

                    else:
                        results = test_system.get_outputs(LANGS[lang], code_input,
                                                          test_inputs=[test_case])  # get_output(code_input, test_case)
                    if type(results) is list:
                        # compilation good
                        comp_mess = [_get_compiler_message(
                            msg[0]) for msg in results]
                        user_output = [r[1] for r in results]
                        test_inputs = [r[2] for r in results]
                        no_tests = len(results)

                    else:
                        # Compilation error
                        test_inputs = None
                        no_tests = 1
                        comp_mess = _get_compiler_message(results[0])
                        user_output = results[1]

                    response = {'compiler': comp_mess,
                                'user_output': user_output,
                                'test_input': test_inputs,
                                'no_tests': no_tests,
                                'is_custom_input': True if test_case != "" else False,
                                'redirect': False,
                                'redirect_url': redirect_url,
                                }
                    print(response)
                    return JsonResponse(response)

            # save to dB every X minutes
            elif 'save_to_db' in request.POST:

                code_input = request.POST.get('code')
                if code_input != '':
                    candidate.add_code({"code": code_input, "is_submitted": False,
                                        'language': lang, 'uid': candidate.unique_id, 'q_num': int_q_num})

        if form.is_valid():
            # submitting code + testing the code against hidden tests
            if request.POST.get("submit_code"):

                verdicts = test_system.get_verdicts(
                    LANGS[lang], code_input, get_all_tests(testing_folder))

                candidate.add_code({"code": code_input, "is_submitted": True, "q_num": int(q_num),
                                    'language': lang, 'uid': candidate.unique_id, "verdicts": json.dumps(verdicts)})
                return redirect(reverse('avaloq:home', kwargs={'u_id': u_id}))

        elif candidate.get_exp(int_q_num) < datetime.datetime.now():
            if lang is not None:
                verdicts = test_system.get_verdicts(
                    LANGS[lang], code_input, get_all_tests(testing_folder))
            else:
                verdicts = ""
            # Final check for timer, extreme case catches
            candidate.add_code({"code": code_input, "is_submitted": True,
                                'language': lang, 'uid': candidate.unique_id, 'q_num': int_q_num,
                                "verdicts": json.dumps(verdicts)})
            return redirect(reverse('avaloq:home', kwargs={'u_id': u_id}))

    elif (candidate.get_exp(int_q_num) < datetime.datetime.now()) or candidate.get_sub(int_q_num):
        # This check is a redirect incase the candidate manages to access the page again, has to occur
        # after the check for ajax and post methods otherwise it may not redirect correctly
        return redirect(reverse('avaloq:home', kwargs={'u_id': u_id}))

    else:
        form = CodeForm()

    context_dict['form'] = form
    return render(request, 'avaloq_app/code.html', context_dict)


@login_required
def review(request):
    context_dict = {}
    context_dict['hostname'] = request.get_host()
    context_dict['reviewer'] = request.user.profile.is_reviewer
    context_dict['admin'] = contextAdmin(request.user)

    # check if any candidates exist
    if(len(Candidate.objects.all()) > 0):
        new_candidate = Candidate.objects.last()

        # Check if a candidate has been created recently and if so, pass it to context dictionary
        if ((datetime.datetime.now() - new_candidate.init_time).total_seconds()) < 8:
            context_dict['newCandidate'] = new_candidate

        context_dict['candidates'] = Candidate.objects.all().order_by(
            '-init_time')

        for c in context_dict['candidates']:
            c.timestamp = datetime.datetime.timestamp(c.init_time)

            if c.is_submitted():
                c.submitted = True

            elif(c.has_started() == False):
                c.submitted = False
            else:
                c.submitted = checkCandidate(c)

            if(c.is_expired() and c.submitted == False):

                c.expired = True
            else:
                c.expired = False

    return render(request, 'avaloq_app/review.html', context=context_dict)


class DeleteCandidateView(View):
    @method_decorator(login_required)
    def get(self, request):
        u_id = request.GET.get('u_id')

        try:
            candidate = Candidate.objects.get(unique_id=u_id)

        except Candidate.DoesNotExist:
            return HttpResponse(-1)

        candidate.delete()
        return HttpResponse(1)


@login_required
def code_review(request, u_id):

    try:
        candidate = Candidate.objects.get(unique_id=u_id)
    except Candidate.DoesNotExist:
        return HttpResponse(-1)

    questions = candidate.questions.all()
    code_entries = []

    for q in questions:
        code_entries.append(Code_Entry.objects.filter(
            candidate=candidate).filter(question=q))

    # get code entries
    entries = []
    verdicts = []
    for snip in code_entries:
        q_entries = []
        for ce in snip:
            # remove extra quotes
            q_entries.append(
                {'final': ce.final, 'code': ce.code, 'language': ce.language})
            if ce.final:
                verdicts.append(ce.verdicts)
        entries.append(q_entries)

    # get verdicts
    v_to_send = []  # parsed verdicts from db to FE
    for q in verdicts:

        q = json.loads(q)
        if type(q) is list:  # comp error
            v_to_send.append(
                [{'compiler': _get_compiler_message(q[0]), 'user_output': q[1]}])

        else:  # list of dict
            question_verdicts = []
            for v in q.keys():
                name = "/".join(v.split('/')[-1:])

                with open(v + '.in', 'r') as file:
                    inp = file.read()

                question_verdicts.append(
                    {'test_case': name,
                     'compiler': _get_compiler_message(q[v][0]),
                     'user_output': q[v][1],
                     'user_input': inp
                     }
                )
            v_to_send.append(question_verdicts)

    # Get question name
    question_titles = []
    for q in questions:
        question_titles.append(q.title)

    context_dict = {}

    context_dict['candidate'] = candidate
    context_dict['admin'] = contextAdmin(request.user)
    context_dict['code_entries'] = json.dumps(entries)
    context_dict['code_length'] = len(entries[0]) - 1
    context_dict['verdicts'] = v_to_send
    context_dict['question1'] = question_titles[0]
    context_dict['question2'] = question_titles[1]

    return render(request, 'avaloq_app/code_review.html', context=context_dict)


@login_required
def add_candidate(request):
    form = CandidateForm()
    if request.method == 'POST':
        form = CandidateForm(request.POST)

        if form.is_valid():

            form.save(commit=True)

            return redirect(reverse('avaloq:review'))
        else:
            print(form.errors)
    return render(request, 'avaloq_app/add_candidate.html', {'form': form})


@login_required
def create_staff(request):
    if request.method == 'POST':
        form = CreateStaff(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            user.profile.is_admin = form.cleaned_data.get('is_admin')
            user.is_staff = form.cleaned_data.get('is_admin')

            user.save()

            return redirect(reverse('avaloq:review'))
    else:
        if not request.user.profile.is_admin:
            return redirect(reverse('avaloq:review'))
        form = CreateStaff()
    return render(request, 'avaloq_app/create_staff.html', {'form': form})


def contextAdmin(user):
    if user.profile.is_admin or user.is_superuser:
        return True
    else:
        return False


def checkCandidate(c):

    if c.is_expired() == False:
        if c.q1_sub and not c.q2_sub and c.q2_start != None:
            if c.q2_exp < datetime.datetime.now():
                return True
            return False

        elif c.q2_sub and not c.q1_sub and c.q1_start != None:
            if c.q1_exp < datetime.datetime.now():
                return True
            return False

        elif not c.q1_sub and not c.q2_sub and c.q1_exp is not None and c.q2_exp is not None:
            if c.q1_exp < datetime.datetime.now() and c.q2_exp < datetime.datetime.now():
                return True
            return False
        else:
            return False
    else:
        return True
