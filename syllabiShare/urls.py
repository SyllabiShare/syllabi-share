from django.urls import path
from . import views

app_name = 'syllabiShare'
urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('search/', views.search, name="search"),
    path('settings/', views.setting, name="setting"),
    path('suggest/', views.suggest, name="suggest"),
    path('upload/', views.upload, name="upload"),
]
