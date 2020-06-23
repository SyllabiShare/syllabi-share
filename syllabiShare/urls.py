from django.urls import path
from . import views
from django.conf import settings

app_name = 'syllabiShare'
urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path(settings.ADMIN_URL, views.admin, name="admin"),
    path('privacy/', views.privacy, name="privacy"),
    path('search/', views.search, name="search"),
    path('settings/', views.setting, name="setting"),
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('suggest/', views.suggest, name="suggest"),
    path('upload/', views.upload, name="upload"),
    path('<slug:dept>/', views.display, name="display"),
    path('view/<slug:domain>/', views.schooladmin, name="schooladmin"),
]
