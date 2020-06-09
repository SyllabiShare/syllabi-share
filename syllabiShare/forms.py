from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator

from crispy_forms.helper import FormHelper


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(help_text='Enter a .edu email address',
                             # RegexValidator matches on an arbitrary subset
                             validators=[RegexValidator(r'\.edu$', message='Email address must end in .edu')],
                             # pattern matches as if wrapped between ^...$
                             widget=forms.EmailInput(attrs={'pattern': r'.*\.edu',
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

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.use_custom_control = False

        return helper


class LoginForm(AuthenticationForm):
    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.use_custom_control = False

        return helper
