import re
import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Application, Category


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        label='ФИО',
        required=True,
        help_text='Введите Фамилию Имя Отчество через пробел'
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': '3-20 латинских букв/цифр, начинается с буквы',
            'email': 'Обязательное поле',
        }

    def __init__(self, *args, **kwargs):  # ИСПРАВЛЕНО: было _init_ (одно подчеркивание)
        super().__init__(*args, **kwargs)


        self.fields['email'].required = True


        self.fields['password1'].help_text = 'Минимум 8 символов, 1 цифра и 1 спецсимвол (!@#$%^&*...)'
        self.fields['password2'].help_text = 'Повторите пароль для подтверждения'

    def clean_full_name(self):
        """Проверка ФИО: минимум 2 слова, кириллица, заглавные буквы"""
        data = self.cleaned_data['full_name'].strip()

        if not data:
            raise forms.ValidationError('ФИО обязательно для заполнения.')


        parts = data.split()


        if len(parts) < 2:
            raise forms.ValidationError('Введите минимум Фамилию и Имя.')


        pattern = r'^[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?$'
        for part in parts:
            if not re.fullmatch(pattern, part):
                raise forms.ValidationError(
                    f'"{part}" — недопустимо. Формат: Кириллица, заглавная в начале. '
                    'Дефис допускается только внутри слова (например: Петров-Сидоров).'
                )

        return data

    def clean_username(self):
        """Проверка логина: 3-20 символов, латиница, начинается с буквы"""
        username = self.cleaned_data['username'].strip()

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]{2,19}$', username):
            raise forms.ValidationError(
                'Логин должен содержать 3-20 латинских букв/цифр и начинаться с буквы. '
                'Допустимы символы: - _'
            )

        return username

    def clean_email(self):
        """Проверка email"""
        email = self.cleaned_data['email'].strip()

        if not email:
            raise forms.ValidationError('Email обязателен для заполнения.')


        if '@' not in email or '.' not in email:
            raise forms.ValidationError('Введите корректный email адрес.')

        return email

    def clean_password1(self):
        """Проверка пароля: минимум 8 символов, 1 цифра, 1 спецсимвол"""
        password = self.cleaned_data.get('password1')

        if not password:
            return password


        if len(password) < 8:
            raise forms.ValidationError('Пароль должен быть не менее 8 символов.')


        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Пароль должен содержать минимум 1 цифру.')


        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        if not any(char in special_chars for char in password):
            raise forms.ValidationError(
                f'Пароль должен содержать минимум 1 спецсимвол: {special_chars}'
            )

        return password


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите вашу заявку подробно...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'photo': 'Фотография (необязательно)',
        }
        help_texts = {
            'photo': 'Максимальный размер: 2 МБ. Форматы: JPG, JPEG, PNG, BMP',
        }

    def clean_photo(self):
        """Проверка загружаемого изображения"""
        photo = self.cleaned_data.get('photo')

        if photo:

            ext = os.path.splitext(photo.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Недопустимый формат файла. Разрешены только: {", ".join(allowed_extensions)}'
                )


            max_size = 2 * 1024 * 1024  # 2 МБ
            if photo.size > max_size:
                raise forms.ValidationError(
                    f'Файл слишком большой. Максимальный размер: {max_size // (1024 * 1024)} МБ'
                )

        return photo

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название категории'
            })
        }
        labels = {
            'name': 'Название категории',
        }
        help_texts = {
            'name': 'Введите уникальное название для категории',
        }

    def clean_name(self):
        """Проверка уникальности названия категории"""
        name = self.cleaned_data.get('name')

        if name:

            if Category.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError('Категория с таким названием уже существует.')

        return name