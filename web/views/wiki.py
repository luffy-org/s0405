from django.shortcuts import render


def wiki(request, project_id):
    return render(request, 'wiki.html')


def add(request, project_id):
    """添加wiki"""
    return render(request, 'wiki.html')