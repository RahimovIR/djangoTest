from django.shortcuts import render
from django.http import HttpResponse

from tables.models import my_models

def home(request):
    context = {'tables': my_models}
    return render(request, 'home.html', context)
