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
from django.conf import settings
from django.contrib.auth.views import LogoutView, LoginView
from syllabiShare.views import SignUpView, ActivateAccount

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True, template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='error.html'), name='logout'),
    path('', include('syllabiShare.urls')),
    path('', include('social_django.urls', namespace='social')),
]

handler404 = 'syllabiShare.views.view404' 