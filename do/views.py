# Create your views here.

import time
import json
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from do.models.task import Task
from do.models.user import Doer
from do.email.emailtask import EmailTaskListener


@login_required
def home(request):
    try:
        email_task_listener = EmailTaskListener('stbeehive.oracle.com', '993',
                                                'venkata.pedapati@oracle.com', 'ZZOiTfByGX0o')
        email_task_listener.get_email_one_day(request.user)
        all_tasks = Task.objects.filter(assignees=request.user)
    except Task.DoesNotExist:
        return render(request, 'do/home.html', {'all_tasks': []})
    return render(request, 'do/home.html', {'all_tasks': all_tasks})


@login_required
def task_detail(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return render(request, 'do/home.html', {'all_tasks': []})
    return render(request, 'do/home.html', {'all_tasks': [task]})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/do/?login=true')


def login_view(request):
    try:
        username = request.POST['useremail_login']
        password = request.POST['password']
    except KeyError:
        return render(request, 'do/newdoer.html', {'show_login_page': True})
    else:
        invalid_login = False
        user = authenticate(username=username, password=password)
        user_account_disabled = False
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/do/home')
            else:
                user_account_disabled = True
        else:
            invalid_login = True
        return render(request, 'do/newdoer.html', {'invalid_login': invalid_login,
                                                   'user_account_disabled': user_account_disabled,
                                                   'show_login_page': True})


def create_user(request):
    try:
        username = request.POST['useremail']
        password = request.POST['password_first']
        first_name, last_name = request.POST['doername'].split(' ', 1)

        try:
            existing_user = Doer.objects.get(email=username)
            response_data = dict()
            response_data['user_exists'] = 'true'
            response_data['user_email'] = existing_user.username
            return HttpResponse(json.dumps(response_data), mimetype='application/json')
        except Doer.DoesNotExist:
            user = Doer.create_user(username, password, username)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponse('{user_exists: "false"}')
    except KeyError:
        try:
            show_login_page = request.GET['login']
        except KeyError:
            return render(request, 'do/newdoer.html')
        return render(request, 'do/newdoer.html', {'show_login_page': True})


@login_required
def create_task(request):
    json_response = {'status': 'failure', 'message': 'Creation of new task failed'}
    try:
        created_by = Doer.objects.get(username=request.user.username)
        assignees_str = request.POST['task_assignees']
        assignees_arr = assignees_str.split(',')
        assignees = [Doer.objects.get(id=assignee_id) for assignee_id in assignees_arr]
        title = request.POST['task_summary']
        primary_desc = request.POST['task_detail']
        task_due_date = request.POST['task_due_date']
    except KeyError:
        return HttpResponse(json.dumps(json_response))
    else:
        task = Task(title=title,
                    created_by=created_by,
                    assignees=assignees,
                    primary_desc=primary_desc,
                    complete_by=datetime.fromtimestamp(time.mktime(time.strptime(task_due_date, "%m/%d/%Y"))))
        task.save()
        json_response['status'] = 'success'
        json_response['message'] = 'Created new task'
        return HttpResponse(json.dumps(json_response))


def people_search(request):
    query_string = request.GET['q']
    try:
        matched_users = Doer.objects(first_name__istartswith=query_string)
        json_response = '['
        separator = ''
        for user in matched_users:
            json_response = json_response + '{"id": "' + str(user.id) + '", "name":"' + \
                            user.first_name + ' ' + user.last_name + '"}' + separator
            separator = ','
        json_response += ']'
        return HttpResponse(json_response)
    except KeyError:
        return HttpResponse("[]")


def user_detail(request, user_id):
    return HttpResponse("User " + user_id)