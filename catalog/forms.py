from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

class CustomUserCreationForm(UserCreationForm):

    full_name = forms.CharField(max_length=100,
                                label='ФИО',
                                help_text='Только кириллические буквы, дефис и пробелы')

    agree_to_terms = forms.BooleanField(required=True,
                                        label='Согласие на обработку персональных данных')

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'agree_to_terms')

        def clean_full_name(self):

            full_name = self.cleaned_data['full_name']
            if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', full_name):
                raise forms.ValidationError('ФИО должно содержать только киррилические буквы, дефис и пробелы')
            return full_name

        def clean_username(self):
            """Проверка логина - только латиница и дефис"""
            username = self.cleaned_data['username']
            if not re.match(r'^[a-zA-Z\-]+$', username):
                raise forms.ValidationError('Логин должен содержать только латинские буквы и дефис')
            return username
