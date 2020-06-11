from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


class SimpleSignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Enter a .edu email address',
                             # RegexValidator matches on an arbitrary subset
                             validators=[RegexValidator(r'\.edu$', message='Email address must end in .edu')],
                             # pattern matches as if wrapped between ^...$
                             widget=forms.EmailInput(attrs={'pattern': r'.*\.edu',
                                                            'title': 'Email address must end in .edu'}))

    class Meta:
        model = User
        fields = [
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


class SignUpForm(SimpleSignUpForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

    @property
    def helper(self):
        helper = super().helper
        helper.layout = Layout(
            'email',
            Row(
                Column('first_name'),
                Column('last_name'),
            ),
            'password1',
            'password2',
        )

        return helper


# Hack around AuthenticationForm to treat their email as their username
class LoginForm(AuthenticationForm):
    username = forms.EmailField()

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].verbose_name = 'email'

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.use_custom_control = False

        return helper
