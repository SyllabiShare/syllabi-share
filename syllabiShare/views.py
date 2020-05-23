from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import timezone
from .models import Submission, School, Suggestion
from django.conf import settings
from django.contrib.auth.models import User


def about(request):
    (template, context) = authenticate(request.user)
    if template:
        if context['loggedIn']:
            logout(request)
        return render(request, template, context)
    return render(request, 'about.html')

def admin(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            if 'purge' in request.POST:
                User.objects.exclude(email__contains=".edu").delete()
            elif 'delete' in request.POST:
                Submission.objects.get(pk=request.POST['pk']).delete()
            elif 'edit' in request.POST:
                edit = Suggestion.objects.get(pk=request.POST['pk'])
                edit.github_issue = request.POST['githubIssue']
                edit.save()
            elif 'recalculate' in request.POST:
                for i in School.objects.all():
                    school = School.objects.filter(domain=i.domain)[0]
                    school.uploads = {}
                    school.save()
                for i in Submission.objects.all():
                    if len(School.objects.filter(domain=i.school)) == 0:
                        entry = School()
                        entry.domain = i.school
                        entry.save()
                    school = School.objects.filter(domain=i.school)[0]
                    school.upload(i.user)
                    school.save()
        return render(request, 'admin.html', {'users':User.objects.all(), 'school': School.objects.all(), 'submissions': Submission.objects.all(), 'suggestions': Suggestion.objects.all()})
    return redirect('/')


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

    school = entry.school
    if not school:
        return render(request, 'school.html', {'first': True})
    elif not entry.reviewed and not user_string == entry.poster:
        return render(request, 'school.html', {'poster': entry.poster,'name': school})

    posts = Submission.objects.filter(school=domain)
    dep = set()
    for i in posts:
        dep.add(i.dept)

    postsDept = []
    for i in sorted(list(dep)):
        postsDept.append(posts.filter(dept=i).order_by('course'))
    return render(request, 'index.html', {'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN, 'leaderboard':entry.topFive(request.user.username),'posts': postsDept,'school':school,'num':len(posts)})


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
    found = Submission.objects.filter(school=get_domain(request.user.email))
    if request.method == 'POST':
        found = found.filter(prof__icontains=request.POST['search']) | found.filter(course__icontains=request.POST['search'])
    return render(request, 'search.html', {'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'posts':found.order_by('course')})


def suggest(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if request.method == 'POST':
        suggestion = Suggestion()
        suggestion.name = request.user
        suggestion.suggestion_text = request.POST['suggestion']
        if 'githubLink' in request.POST and 'https://github.com/verndrade/syllabi-share/issues/' in request.POST['githubLink']:
            suggestion.github_issue = request.POST['githubLink']
        suggestion.save()
    return render(request, 'suggest.html', {'suggestion':Suggestion.objects.all()})


def upload(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)
    success = False
    message = 'Misuse of uploads will be met by a ban!'
    if request.method == 'POST':
        course = request.POST['prof'].split()
        goodProf = len(request.POST['prof'].split()) == 2 and course[0].isalpha() and course[1].isalpha()
        course = request.POST['course'].split()
        goodCourse = len(course) == 2 and course[0].isalpha() and course[1].isnumeric()
        if goodProf and goodCourse:
            entry = Submission()
            entry.user = request.user.username
            entry.school = get_domain(request.user.email)
            entry.prof = request.POST['prof']
            entry.course = request.POST['course'].upper()
            entry.dept = course[0].upper()
            entry.upvotes = 1
            entry.syllabus = request.FILES['file']
            entry.save()
            school = School.objects.filter(domain=entry.school)[0]
            school.upload(request.user.username)
            school.save()
            success = True
        elif goodProf:
            message = 'Course not valid! Try "Mnemonic Number" Format'
        elif goodCourse:
            message = 'Professor name not valid! Try "FirstName LastName" Format'
        else:
            message = 'Input not valid! Try Again'
    return render(request, 'upload.html', {'success': success, 'message': message})


def view404(request, exception=None):
    return redirect('/')
