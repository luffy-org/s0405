from django.http import HttpResponse
from django.shortcuts import render


def dashboard(request, project_id):
    return render(request, 'dashboard.html')


def statistics(request, project_id):
    return render(request, 'dashboard.html')


def issues(request, project_id):
    return render(request, 'dashboard.html')


def setting(request, project_id):
    return render(request, 'dashboard.html')




