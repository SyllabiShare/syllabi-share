from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import timezone
from .models import Submission, School, Suggestion
from django.conf import settings


def about(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)
    return render(request, 'about.html')


def authenticate(user):
    if not user.is_authenticated:
        return ('error.html', {'loggedIn': False})
    if user.email[-4:] != '.edu':
        return ('error.html', {'loggedIn': True})
    return (False, False)


def get_domain(email):
    start = email.index('@') + 1
    end = email.index('.edu')
    domain = email[start:end]
    if len(School.objects.filter(domain=domain)) == 0:
        school = School()
        school.domain = domain
        school.save()
    return domain


def index(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)
    domain = get_domain(request.user.email)
    entry = School.objects.get(domain=domain)
    user_string = str(request.user)

    if request.method == 'POST':
        if 'name' in request.POST:
            entry.add_school(request.POST['name'], user_string)
        else:
            entry.review()
        entry.save()

    if not entry.school:
        return render(request, 'school.html', {'first': True})
    elif not entry.reviewed and not user_string == entry.poster:
        return render(request, 'school.html', {'poster': entry.poster,'name': entry.school})
    return render(request, 'index.html', {'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN, 'leaderboard':School.objects.filter(domain=domain)[0].topFive(request.user.username),'posts':Submission.objects.filter(school=domain)})


def setting(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)
    return render(request, 'settings.html')


def search(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)
    found = Submission.objects.filter(school=get_domain)
    if request.method == 'POST':
        found = found.filter(prof__icontains=request.POST['search']) | found.filter(course__icontains=request.POST['search'])
    return render(request, 'search.html', {'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'posts':found.order_by()})


def suggest(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if request.method == 'POST':
        suggestion = Suggestion()
        suggestion.name = request.user
        suggestion.suggestion_text = request.POST['suggestion']
        suggestion.save()
    return render(request, 'suggest.html', {'suggestion':Suggestion.objects.all()})


def upload(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)
    success = False
    if request.method == 'POST':
        entry = Submission()
        entry.user = request.user.username
        entry.school = get_domain(request.user.email)
        entry.prof = request.POST['prof']
        entry.course = request.POST['course']
        entry.upvotes = 1
        entry.syllabus = request.FILES['file']
        entry.save()
        school = School.objects.filter(domain=entry.school)[0]
        school.upload(request.user.username)
        school.save()
        success = True
    return render(request, 'upload.html', {'success': success})


def view404(request, exception=None):
    return redirect('/')
