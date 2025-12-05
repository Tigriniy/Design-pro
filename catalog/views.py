from gc import get_objects

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CategoryForm

from .forms import CustomUserCreationForm, ApplicationForm, Category
from .models import Application


def index(request):
    completed_applications = Application.objects.filter(
        status='выполнено'
    ).select_related('category').order_by('-created_at')[:4]

    in_progress_count = Application.objects.filter(status='в работе').count()

    return render(request, 'catalog/index.html', {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    })


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
    template_name = 'catalog/application_form.html'
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


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_applications(request):
    qs = Application.objects.all().select_related('user', 'category')
    status = request.GET.get('status')
    if status in ['новая', 'в работе', 'выполнено']:
        qs = qs.filter(status=status)

    # Обработка POST: смена статуса
    if request.method == 'POST' and request.POST.get('action') == 'change_status':
        app_id = request.POST.get('app_id')
        if not app_id:
            messages.error(request, 'Не указана заявка для изменения')
            return redirect('admin_applications')
        new_status = request.POST.get('status')
        app = get_object_or_404(Application, id=app_id)
        app.status = new_status
        app.save()
        messages.success(request, f'Статус заявки «{app.title}» изменён на «{app.get_status_display()}»')
        return redirect('admin_applications')

    return render(request, 'catalog/admin_applications.html', {
        'applications': qs,
        'selected_status': status,
    })


@user_passes_test(is_admin)
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'catalog/admin_categories.html', {'categories': categories})


@user_passes_test(is_admin)
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория добавлена')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'catalog/admin_category_form.html', {'form': form})


@user_passes_test(is_admin)
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'catalog/admin_category_form.html', {'form': form, 'category': category})


@user_passes_test(is_admin)
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        count = category.application_set.count()
        category.delete()  # ← CASCADE удалит все заявки!
        messages.success(request, f'Категория «{name}» и {count} заявок удалены')
        return redirect('admin_categories')
    return render(request, 'catalog/admin_category_confirm_delete.html', {'object': category})
