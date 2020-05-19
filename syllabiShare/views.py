from django.shortcuts import render,redirect
from django.contrib.auth import logout

import requests

def index(request):
    if not request.user.is_authenticated:
        return render(request, "error.html", {'loggedIn':False})
    if request.user.email[-4:] != '.edu':
        logout(request)
        return render(request, "error.html", {'loggedIn':True})
    return render(request, "index.html")

def search(request):
    if not request.user.is_authenticated:
        return render(request, "error.html", {'loggedIn':False})
    if request.user.email[-4:] != '.edu':
        logout(request)
        return render(request, "error.html", {'loggedIn':True})
    return render(request, "search.html")

def upload(request):
    if not request.user.is_authenticated:
        return render(request, "error.html", {'loggedIn':False})
    if request.user.email[-4:] != '.edu':
        logout(request)
        return render(request, "error.html", {'loggedIn':True})
    return render(request, "upload.html")

def view404(request, exception=None):
    return redirect('/')
