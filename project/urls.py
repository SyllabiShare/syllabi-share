"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views

from syllabiShare.forms import LoginForm
from syllabiShare import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', views.ActivateAccount.as_view(), name='activate'),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm,
                                                redirect_authenticated_user=True,
                                                template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='landing.html'), name='logout'),
    path('registration/', include([
        path('', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ])),
    path('', include('syllabiShare.urls')),
]

handler404 = 'syllabiShare.views.view404'
