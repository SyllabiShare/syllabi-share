from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(help_text='Enter a .edu email address',
                             validators=[RegexValidator(r'.*\.edu$', message='Email address must end in .edu')],
                             widget=forms.EmailInput(attrs={'pattern': r'.*\.edu$',
                                                            'title': 'Email address must end in .edu'}))

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
        ]
