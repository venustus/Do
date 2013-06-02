# Create your views here.
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.contrib.auth import authenticate, login
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

def login_view(request):
    try:
        username = request.POST['username']
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

def create_user(request):
    try:
        username = request.POST['email']
        password = request.POST['password']
        first_name, last_name = request.POST['name'].split()
        user = Doer.create_user(username, password, username)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return HttpResponseRedirect('/do/home')
    except KeyError:
        return render(request, 'do/newdoer.html')

@login_required
def task_detail(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except:
        raise Http404
    return render(request, 'do/detail.html', {'task': task})

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
