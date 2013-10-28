# Create your views here.

import time
import json
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from do.models.task import Task, TaskStatus
from do.models.user import Doer
from do.models.project import Project


def home(request):
    return render(request, 'do/base.html')


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
    return HttpResponseRedirect('/do/login')


def login(request):
    try:
        username = request.POST['useremail_login']
        password = request.POST['password']
    except KeyError:
        return render(request, 'do/login.html')
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
        return render(request, 'do/login.html', {'invalid_login': invalid_login,
                                                 'user_account_disabled': user_account_disabled})

def doesUserExist(request, useremail):
    try:
        responseData = dict()
        responseData['user_exists'] = 'true'
        try:
            user = Doer.objects.get(email=useremail)
            responseData['id'] = 1
            return HttpResponse(json.dumps(responseData), mimetype='application/json')
        except Doer.DoesNotExist:
            responseData['user_exists'] = 'false'
            responseData['id'] = 0
            return HttpResponse(json.dumps(responseData), mimetype='application/json')
    except KeyError:
        return HttpResponse('Invalid request')

def signupAndLogin(request):
    try:
        username = request.POST['useremail']
        password = request.POST['password_first']
        firstName, lastName = request.POST['doername'].split(' ', 1)

        try:
            existingUser = Doer.objects.get(email=username)
            responseData = dict()
            responseData['user_exists'] = 'true'
            responseData['user_email'] = existingUser.username
            return HttpResponse(json.dumps(responseData), mimetype='application/json')
        except Doer.DoesNotExist:
            user = Doer.create_user(username, password, username)
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/do/')
    except KeyError:
        return render(request, 'do/newdoer.html')


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
                    status=TaskStatus.IN_PROGRESS,
                    complete_by=datetime.fromtimestamp(time.mktime(time.strptime(task_due_date, "%m/%d/%Y"))))
        task.save()
        json_response['status'] = 'success'
        json_response['message'] = 'created new task'
        return HttpResponse(json.dumps(json_response))


@login_required
def create_project(request):
    json_response = {'status': 'failure', 'message': 'new project cannot be created'}
    try:
        project_name = request.POST['project_name']
        assignees_str = request.POST['project_assignees']
        assignees_arr = assignees_str.split(',')
        assignees = [Doer.objects.get(id=assignee_id) for assignee_id in assignees_arr]
        start_date = request.POST['start_date']
        etc = request.POST['etc']
    except KeyError:
        return HttpResponse(json.dumps(json_response))
    else:
        project = Project(name=project_name,
                          members=assignees,
                          start_date=datetime.fromtimestamp(time.mktime(time.strptime(start_date, "%m/%d/%Y"))),
                          estimated_time_for_completion_weeks=int(etc))
        project.save()
        json_response['status'] = 'success'
        json_response['message'] = 'added new project'
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


@login_required
def task_quick_edit(request, task_id):
    json_response = {'status': 'failure', 'message': 'cannot save task'}
    try:
        task = Task.objects.get(id=task_id)
        is_completed = request.POST['status']
        is_due_today = request.POST['today']
        is_important = request.POST['important']
        is_urgent = request.POST['urgent']
        if is_completed == 'done':
            task.completed()
        if is_important == 'yes':
            task.is_important = True
        if is_urgent == 'yes':
            task.is_urgent = True
        if is_due_today == 'yes':
            task.complete_by = datetime.now().replace(hour=23, minute=59, second=59)
        task.save()
        json_response['status'] = 'success'
        json_response['message'] = 'task marked completed'
        return HttpResponse(json.dumps(json_response))
    except Task.DoesNotExist:
        return HttpResponse("[]")


def user_detail(request, user_id):
    return HttpResponse("User " + user_id)