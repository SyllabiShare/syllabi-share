from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import timezone
from .models import Submission, School, Suggestion
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.contrib import messages
from django.http import HttpResponseRedirect


def about(request):
    return render(request, 'about.html')

def admin(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            if 'purge' in request.POST:
                User.objects.exclude(email__contains=".edu").delete()
            elif 'delete' in request.POST:
                Submission.objects.get(pk=request.POST['pk']).delete()
            elif 'toggleHide' in request.POST:
                submission = Submission.objects.get(pk=request.POST['pk'])
                submission.toggleHidden()
                submission.save()
            elif 'close' in request.POST:
                Suggestion.objects.get(pk=request.POST['pk']).delete()
            elif 'takedown' in request.POST and 'reason' in request.POST:
                school = School.objects.get(pk=request.POST['pk'])
                school.takedown = True
                school.reason = request.POST['reason']
                school.save()
            elif 'edit' in request.POST:
                edit = Suggestion.objects.get(pk=request.POST['pk'])
                edit.github_issue = request.POST['githubIssue']
                edit.save()
            elif 'sendtestmail' in request.POST and 'password' in request.POST and 'body' in request.POST:
                if request.POST['password'] == settings.EMAIL_PASSWORD:
                    data = [
                        ("SyllabiShare", request.POST['body'], "syllabishare@gmail.com", ['syllabishare@gmail.com'])
                    ]
                    send_mass_mail(data)
                    return render(request, 'admin.html', {'users':User.objects.all(), 'school': School.objects.all(), 'submissions': Submission.objects.all(), 'suggestions': Suggestion.objects.all(), 'emailBody': request.POST['body']})
            elif 'sendmassmail' in request.POST and 'password' in request.POST and 'body' in request.POST:
                if request.POST['password'] == settings.EMAIL_PASSWORD:
                    all_users = User.objects.all()
                    data = [
                        ("SyllabiShare", request.POST['body'], "syllabishare@gmail.com", [user.email]) for user in all_users
                    ]
                    send_mass_mail(data)
                    return render(request, 'admin.html', {'users':User.objects.all(), 'school': School.objects.all(), 'submissions': Submission.objects.all(), 'suggestions': Suggestion.objects.all(), 'mailSuccess': True})
        return render(request, 'admin.html', {'users':User.objects.all(), 'school': School.objects.all(), 'submissions': Submission.objects.all(), 'suggestions': Suggestion.objects.all()})
    return redirect('/')

def authenticate(user):
    if not user.is_authenticated:
        return ('error.html', {'loggedIn': False})
    if not user.profile.school:
        return ('error.html', {'loggedIn': True})

    school = user.profile.school
    if school.takedown:
        return ('sorry.html', {'loggedIn': True, 'reason': school.reason, 'domain': user.email[user.email.index('@') + 1:]})
    return (False, False)

def display(request, dept=None):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)
    posts = Submission.objects.filter(school=request.user.profile.school).filter(dept=dept.upper()).filter(hidden=False).order_by('number')
    if not dept or len(posts) == 0:
        return redirect('/')
    return render(request, 'display.html', {'posts': posts, 'dept':dept,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN})


def index(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)

    school = request.user.profile.school
    if request.method == 'POST':
        if 'name' in request.POST:
            school.add_school(request.POST['name'], request.user.username)
        else:
            school.review()
        school.save()

    if not school.name:
        return render(request, 'school.html', {'first': True})
    elif not school.reviewed and not request.user.username == school.creator:
        return render(request, 'school.html', {'name': school.name})

    posts = Submission.objects.filter(school=school).filter(hidden=False)
    if len(posts) == 0:
        return redirect('syllabiShare:upload')

    dep = set()
    for i in posts:
        dep.add(i.dept)
    return render(request, 'index.html', {'leaderboard':school.topFive(),'posts':sorted(list(dep)),'school':school.name,'num':len(posts)})


def privacy(request):
    return render(request, 'privacy.html')


def schooladmin(request,domain=None):
    if request.user.is_superuser:
        school = None
        try:
            school = School.objects.get(domain=domain)
        except:
            return redirect('/')
        posts = Submission.objects.filter(school=school).filter(hidden=False)
        dep = set()
        for i in posts:
            dep.add(i.dept)
        return render(request, 'index.html', {'leaderboard':school.topFive(),'posts':sorted(list(dep)),'school':domain,'num':len(posts)})
    return redirect('/')


def search(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)

    found = Submission.objects.filter(school=request.user.profile.school).filter(hidden=False)
    if request.method == 'POST':
        found = found.filter(prof__icontains=request.POST['search']) | found.filter(course__icontains=request.POST['search']) | found.filter(title__icontains=request.POST['search'])
    dep = set()
    for i in found:
        dep.add(i.dept)
    return render(request, 'display.html', {'posts':found.order_by('course'),'dept':dep,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'search': True,'school':request.user.profile.school.name})


def setting(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)

    if request.method == 'POST':
        if 'username' in request.POST:
            if request.user.username == request.POST['username']:
                logout(request)
                User.objects.get(username=request.POST['username']).delete()
                return render(request, 'error.html')
    return render(request, 'settings.html')


def suggest(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if request.method == 'POST':
        suggestion = Suggestion()
        suggestion.name = request.user
        suggestion.suggestion_text = request.POST['suggestion']
        if 'githubLink' in request.POST and 'https://github.com/SyllabiShare/syllabi-share/issues/' in request.POST['githubLink']:
            suggestion.github_issue = request.POST['githubLink']
        suggestion.save()
        return HttpResponseRedirect("/suggest") # prevents re-post on refresh problem 
    return render(request, 'suggest.html', {'suggestion':Suggestion.objects.all()})


def upload(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)
    if request.method == 'POST':
        prof = request.POST['prof'].strip().split()
        goodProf = len(prof) == 2 and all(char.isalpha() or char == '-' or char == '\'' for char in prof[0]) and all(char.isalpha() or char == '-' or char == '\'' for char in prof[1])
        if goodProf:
            entry = Submission()
            entry.user = request.user
            entry.school = request.user.profile.school
            entry.prof = prof[0] + ' ' + prof[1]
            entry.title = request.POST['title']
            entry.dept = request.POST['dept'].strip().upper()
            entry.number = request.POST['number']
            entry.semester = request.POST['semester']
            entry.year = request.POST['year']
            entry.upvotes = 1
            entry.hidden = True
            entry.syllabus = request.FILES['file']
            entry.syllabus.name = '_'.join([prof[0].lower(), prof[1].lower(), entry.dept.lower(), entry.number, entry.semester, entry.year]) + '.pdf'
            entry.save()
            messages.success(request, 'Syllabus successfully added. Thank you!')
        else:
            messages.error(request, 'Please enter the professor\'s name as "FirstName LastName"')
        return HttpResponseRedirect("/upload") # prevents re-post on refresh problem 
    return render(request, 'upload.html')


def view404(request, exception=None):
    return redirect('/')

