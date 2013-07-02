# Create your views here.

import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from do.models.task import Task
from do.models.user import Doer

@login_required
def home(request):
    try:
        all_tasks = Task.objects.filter(assignees=request.user)
    except Task.DoesNotExist:
        return render(request, 'do/home.html', {'all_tasks': []})
    return render(request, 'do/home.html', {'all_tasks': all_tasks})

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
        first_name, last_name = request.POST['doername'].split()

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
    try:
        created_by = Doer.objects.get(username=request.POST['created_by'])
        assigned_to = Doer.objects.get(username=request.POST['assigned_to'])
        title = request.POST['title']
        primary_desc = request.POST['primary_desc']
    except KeyError:
        return render(request, 'do/create.html')
    else:
        task = Task(title=title,
                    created_by=created_by,
                    assignees=[assigned_to],
                    primary_desc=primary_desc)
        task.save()
        return HttpResponseRedirect('/do/' + str(task.id))


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