from django.shortcuts import render
from django.urls import path
from . import  views

urlpatterns = [
    path('', views.index, name='index'),
]

def index(request):
    """Главная страница сайта"""
    return render(request, 'index.html')