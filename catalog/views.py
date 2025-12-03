
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm  # импортируем нашу форму
from django.contrib import messages

def index(request):
    return render(request, 'catalog/index.html')

def register(request):

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

def user_login(request):
    if request.method == 'POST':
        form=AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            """если логин  пароль правильные"""

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')


            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request,f'Добро пожаловать, {username}!')
                return redirect('index')

    else:

        form = AuthenticationForm()

    return render(request, 'catalog/login.html', {'form': form})


