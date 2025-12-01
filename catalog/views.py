
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm  # импортируем нашу форму
from django.contrib import messages
def index(request):
    """Главная страница сайта"""
    return render(request, 'catalog/index.html')

def register(request):
    """"Представление для регистрации новых пользователей
    Обрбатывает форму регистрации"""

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():

        user = form.save()

        login(request, user)

        messages.success(request, 'регистрация прошла успешно!')

        return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'catalog/register.html', {'form': form})

def user