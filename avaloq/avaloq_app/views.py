import os
from pathlib import Path

from django.shortcuts import render, redirect
from django.urls import reverse
from itertools import chain
import datetime
import time

# import functions for testing
# from solution import get_output, get_verdicts
from sys import platform


from avaloq_app.testutil import get_all_tests, get_sample_tests, get_inputs

if platform == "linux" or platform == "linux2":
    from avaloq_app.testsystem import TestSystem, LANGS  # get_output, get_verdicts
else:
    from avaloq_app.fakesystem import TestSystem, LANGS  # get_output, get_verdicts

from django.http import HttpResponse, JsonResponse
from django.views import View
from avaloq_app.models import Question, Candidate, CodeTemplate, Code_Entry
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CodeForm, CandidateForm, CreateStaff

import json
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")
test_case_path = config['PATHS']['test_cases']

question_folder = os.path.join(Path(__file__).resolve().parent.parent, 'tasks/questions')

test_system = TestSystem()

def expired(request):
    return render(request, 'avaloq_app/expired.html')

def completion(request):
    context_dict = {}
    return render(request, 'avaloq_app/completion.html', context=context_dict)


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

    context_dict['exp_time'] = int(time.mktime(candidate.get_exp(int_q_num).timetuple())) * 1000

    # ----- get question path -----
    question_text = candidate.questions.values('text')[int_q_num][
        'text']  # str(Question.objects.get(id=candidate.question_id))
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
    # print(templates)
    context_dict["templates"] = json.dumps(templates)

    if request.method == 'POST' or request.is_ajax:

        form = CodeForm(request.POST)
        print(form.is_valid)
        print(form.errors)

        code_input = form.cleaned_data['code_text']
        
        test_case = form.cleaned_data['test_input']
        lang = request.POST.get('language')
        testing_folder = os.path.join('tasks/test_cases/', str(candidate.questions.all()[int(q_num)].q_id))
        
        redirect_url = reverse('avaloq:home', kwargs={'u_id': u_id})

        if request.is_ajax():
            # initial back end timer check, if the time has expired return a response to js file to do a redirect
            if (candidate.get_exp(int_q_num) < datetime.datetime.now()):

                if lang is not None:
                    verdicts = test_system.get_verdicts(LANGS[lang], code_input, get_all_tests(testing_folder))
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
                print(candidate.get_exp(int_q_num))

                response = {'redirect': False,
                            'exp_time': context_dict['exp_time'],
                            }
                return JsonResponse(response)
            # running code against user's input or sample inputs

            elif 'user_test_input' in request.POST:
                print("test")
                form = CodeForm(request.POST)
                print(form.is_valid)
                print(form.errors)

                if form.is_valid():
                    lang = form.cleaned_data['language']  # for future use
                    user_test_input = form.cleaned_data['user_test_input']

                    if not user_test_input: #if it brakes use: request.POST.get('user_test_input')
                    
                        
                        results = test_system.get_outputs(LANGS[lang], code_input, get_inputs(
                            get_sample_tests(testing_folder)))  # get_output(code_input, test_case)
                    else:
                        results = test_system.get_outputs(LANGS[lang], code_input,
                                                          [test_case])  # get_output(code_input, test_case)
                    if type(results) is list:
                        # compilation good
                        comp_mess = [_get_compiler_message(msg[0]) for msg in results]
                        user_output = [r[1] for r in results]
                        test_inputs = [r[2] for r in results]
                        no_tests = len(results)
                        print(comp_mess)
                        print(user_output)
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
                    return JsonResponse(response)
                print("----------- END RUN CODE----------------------------")

            elif 'save_to_db' in request.POST:

                print("----------- TIME AJAX----------------------------")
                code_input = request.POST.get('code')
                if code_input != '':
                    candidate.add_code({"code": code_input, "is_submitted": False,
                                    'language': lang, 'uid': candidate.unique_id, 'q_num': int_q_num})
                print("----------- END TIME AJAX----------------------------")

        if form.is_valid():
            # submitting code + testing the code against hidden tests
            if request.POST.get("submit_code"):
                print("pressed submit code")
                code_input = form.cleaned_data['code_text']
                lang = form.cleaned_data['language']
                
                verdicts = test_system.get_verdicts(LANGS[lang], code_input, get_all_tests(testing_folder))

                candidate.add_code({"code": code_input, "is_submitted": True, "q_num": int(q_num),
                                    'language': lang, 'uid': candidate.unique_id, "verdicts": json.dumps(verdicts)})
                return redirect(reverse('avaloq:home', kwargs={'u_id': u_id}))

        elif (candidate.get_exp(int_q_num) < datetime.datetime.now()):
            if lang is not None:
                verdicts = test_system.get_verdicts(LANGS[lang], code_input, get_all_tests(testing_folder))
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
    

    # Check if a candidate has been created recently and if so, pass it to context dictionary
    new_candidate = Candidate.objects.last()
    if((datetime.datetime.now() - new_candidate.init_time).total_seconds()) < 8:
        context_dict['newCandidate'] = new_candidate



    
    
    context_dict['hostname'] = request.get_host()
    

    context_dict['reviewer'] = request.user.profile.is_reviewer

    context_dict['admin'] = contextAdmin(request.user)

    context_dict['candidates'] = Candidate.objects.all().order_by('-init_time')

    for c in context_dict['candidates']:
        c.timestamp = datetime.datetime.timestamp(c.init_time)
        print(c)

        if(c.is_submitted()):
            c.submitted = True
        elif(c.has_started()==False):
            c.submitted = False
        else:
            c.submitted = checkCandidate(c)

        if(c.is_expired() and c.submitted==False):
            c.expired=True
        else:
            c.expired=False
       

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
    print(u_id)
    try:
        candidate = Candidate.objects.get(unique_id=u_id)
    except Candidate.DoesNotExist:
        print("hellasdlkf")
        return HttpResponse(-1)

    questions = candidate.questions.all()
    # all_code_entries = Code_Entry.objects.filter(candidate=candidate).filter(question=q)
    code_entries = []
    print("aaaaaa")
    for q in questions:
        print("laskdjf")
        code_entries.append(Code_Entry.objects.filter(candidate=candidate).filter(question=q))
        # code_entries.append(all_code_entries.filter(question=q))

    print("code entries: ", code_entries)
    entries = []
    verdicts = []
    for snip in code_entries:
        q_entries = []
        for ce in snip:
            q_entries.append({'final': ce.final, 'code': ce.code, 'language': ce.language})  # remove extra quotes
            if ce.final:
                verdicts.append(ce.verdicts)
        entries.append(q_entries)

    v_to_send = [] # parsed verdicts from db to FE
    for q in verdicts:
        print("verdicts: ", q)
        q = json.loads(q)
        if type(q) is list: #comp error
            v_to_send.append([{'compiler' : _get_compiler_message(q[0]), 'user_output': q[1]}])

        else: # list of dict
            question_verdicts=[]
            for v in q.keys():
                name = "/".join(v.split('/')[-1:])

                with open(v+'.in', 'r') as file:
                    inp = file.read()
                # print(inp)
                question_verdicts.append(
                    {'test_case':name,
                     'compiler': _get_compiler_message(q[v][0]),
                     'user_output': q[v][1],
                     'user_input': inp
                    }
                )
            v_to_send.append(question_verdicts)



    context_dict = {}

    context_dict['candidate'] = candidate
    context_dict['admin'] = contextAdmin(request.user)
    context_dict['code_entries'] = json.dumps(entries)
    context_dict['code_length'] = len(entries[0]) - 1
    context_dict['verdicts'] = v_to_send

    return render(request, 'avaloq_app/code_review.html', context=context_dict)

@login_required
def add_candidate(request):
    form = CandidateForm()
    if request.method=='POST':
        form=CandidateForm(request.POST)

        if form.is_valid():
            
            form.save(commit=True)

            return redirect(reverse('avaloq:review'))
        else:
            print (form.errors)
    return render(request,'avaloq_app/add_candidate.html', {'form':form})


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
        if request.user.profile.is_admin == False:
            return redirect(reverse('avaloq:review'))
        form = CreateStaff()
    return render(request, 'avaloq_app/create_staff.html', {'form': form})

def contextAdmin(user):
    if (user.profile.is_admin or user.is_superuser):
        return True
    else:
        return False


def checkCandidate(c):
    if(c.is_expired()==False):
        if(c.q1_sub and not c.q2_sub and c.q2_start!=None and c.q2_exp<datetime.datetime.now()):
            return True
        elif(c.q2_sub and not c.q1_sub and c.q1_start!=None and c.q1_exp<datetime.datetime.now()):
            return True
        elif(not c.q1_sub and not c.q2_sub and c.q1_exp<datetime.datetime.now() and c.q2_exp<datetime.datetime.now()):
            return True
        else:
            return False
    else:
        return True