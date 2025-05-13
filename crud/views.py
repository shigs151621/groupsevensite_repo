from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse('Hello World!')

def test(request):
    return render(request, 'layout/base.html')