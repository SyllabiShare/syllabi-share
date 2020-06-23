from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator

from crispy_forms.helper import FormHelper
from django.urls import reverse
from django.utils.safestring import mark_safe


class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Enter a .edu email address',
                             # RegexValidator matches on an arbitrary subset
                             validators=[RegexValidator(r'\.edu$', message='Email address must end in .edu')],
                             # pattern matches as if wrapped between ^...$
                             widget=forms.EmailInput(attrs={'pattern': r'.*\.edu',
                                                            'title': 'Email address must end in .edu'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('%(email)s already has an account',
                                        code='duplicate_email',
                                        params={'email': email})
        return email

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


# Hack around AuthenticationForm to treat their email as their username
class LoginForm(AuthenticationForm):
    username = forms.EmailField()

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].verbose_name = 'email'

    def confirm_login_allowed(self, user):
        if not user.profile.email_confirmed:
            raise forms.ValidationError(mark_safe("Please confirm your email before signing in. Didn't receive an "
                                                  f'email? <a href="{reverse("resend_confirmation")}">Send it again</a>'), code='unconfirmed')

        super().confirm_login_allowed(user)

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.use_custom_control = False

        return helper


class ConfirmationEmailForm(forms.Form):
    email = forms.EmailField()

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.use_custom_control = False

        return helper
