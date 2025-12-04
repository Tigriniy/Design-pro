# catalog/forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        label='ФИО',
        required=True
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных'
    )

    class Meta:
        model = User
        fields = ('username', 'email')


    def clean_full_name(self):
        data = self.cleaned_data['full_name'].strip()
        if not data:
            raise forms.ValidationError('ФИО обязательно.')

        parts = data.split()
        if len(parts) != 3:
            raise forms.ValidationError('Требуется ровно 3 слова: Фамилия Имя Отчество.')


        pattern = r'^[А-ЯЁ][а-яё]*(-[А-ЯЁ][а-яё]*)?$'

        for part in parts:
            if not re.fullmatch(pattern, part):
                raise forms.ValidationError(
                    f'«{part}» — недопустимо. Допустимы только кириллические буквы, '
                    'заглавная в начале, один дефис внутри (например: Смирнов, Иванов-Петров).'
                )
        return data

    def clean_username(self):
        u = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_\-]{2,19}$', u):
            raise forms.ValidationError('Логин: 3–20 лат. букв/цифр, начинается с буквы.')
        return u