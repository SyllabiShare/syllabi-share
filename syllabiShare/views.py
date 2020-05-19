from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.utils import timezone
from .models import Submission

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
    if request.method == 'POST':
        entry = Submission()
        entry.user = request.user.username
        entry.prof = request.POST['prof']
        entry.course = request.POST['course']
        entry.upvotes = 1
        entry.add_date = timezone.now()
    if not request.user.is_authenticated:
        return render(request, "error.html", {'loggedIn':False})
    if request.user.email[-4:] != '.edu':
        logout(request)
        return render(request, "error.html", {'loggedIn':True})
    return render(request, "upload.html")

def view404(request, exception=None):
    return redirect('/')
