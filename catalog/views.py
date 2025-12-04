from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, ApplicationForm, Category
from .models import Application


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



@login_required
def profile(request):
    return render(request, 'catalog/profile.html')

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'catalog/application_create.html'
    success_url = reverse_lazy('my_applications')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'новая'
        return super().form_valid(form)


class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'catalog/application_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        qs = Application.objects.filter(user=self.request.user)
        status = self.request.GET.get('status')
        if status in ['новая', 'в работе', 'выполнено']:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'catalog/application_confirm_delete.html'
    success_url = reverse_lazy('my_applications')

    def get_queryset(self):

        return Application.objects.filter(
            user=self.request.user,
            status='новая'
        )
