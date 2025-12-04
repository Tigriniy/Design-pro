from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm



def index(request):
    return render(request, 'catalog/index.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.profile.full_name = form.cleaned_data['full_name']
            user.profile.agree_to_terms = form.cleaned_data['agree_to_terms']
            user.profile.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.profile.full_name}!')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'catalog/register.html', {'form': form})


def user_login(request):

    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import authenticate
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'catalog/login.html', {'form': form})