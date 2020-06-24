from .forms import SignUpForm, SimpleSignUpForm
from .models import Submission, School, Suggestion, UserProfile
from .tokens import account_activation_token
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mass_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View, UpdateView


class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            messages.success(request, 'Your account has been confirmed')
            return redirect('syllabiShare:index')
        else:
            # TODO: Throwing them back to the home page doesn't seem too helpful here.
            # They should have a way of regenerating an email.
            messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used')
            return redirect('syllabiShare:index')


class SignUpView(View):
    form_class = SignUpForm
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your SyllabiShare Account'
            message = render_to_string('emails/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'confirm-account.html', {'host': settings.EMAIL_HOST_USER, 'email': user.email})
        return render(request, self.template_name, {'form': form})


def about(request):
    return render(request, 'about.html')


def admin(request):
    if not request.user.is_superuser:
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
        return render(request, 'admin.html', {'users':UserProfile.objects.all(), 'school': School.objects.all(), 'submissions': Submission.objects.all(), 'suggestions': Suggestion.objects.all()})
    return redirect('/')


def authenticate(user):
    if not user.is_authenticated:
        return ('landing.html', {'form': SimpleSignUpForm()})

    school = user.profile.school
    if school.takedown:
        return ('sorry.html', {'reason': school.reason, 'domain': user.email[user.email.index('@') + 1:]})
    return (False, False)


def display(request, dept=None):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if request.method == 'POST':
        if 'save' in request.POST:
            request.user.profile.saved.add(Submission.objects.get(pk=request.POST['pk']))
        if 'unsave' in request.POST:
            request.user.profile.saved.remove(Submission.objects.get(pk=request.POST['pk']))

    posts = Submission.objects.filter(school=request.user.profile.school).filter(dept=dept.upper()).filter(hidden=False).order_by('number')
    if not dept or len(posts) == 0:
        return redirect('/')
    return render(request, 'display.html', {'posts': posts, 'dept':dept,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN})


def index(request):
    (template, context) = authenticate(request.user)
    if template:
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


def saved(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if 'unsave' in request.POST:
        request.user.profile.saved.remove(Submission.objects.get(pk=request.POST['pk']))

    found = request.user.profile.saved.filter(hidden=False)

    return render(request, 'display.html', {'posts':found.order_by('dept','number'), 'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'saved': True, 'school':request.user.profile.school.name})


def search(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    found = Submission.objects.filter(school=request.user.profile.school).filter(hidden=False)
    if request.method == 'POST':
        if 'save' in request.POST:
            request.user.profile.saved.add(Submission.objects.get(pk=request.POST['pk']))
        found = found.filter(prof__icontains=request.POST['search']) | found.filter(dept__icontains=request.POST['search']) | found.filter(title__icontains=request.POST['search'])
    dep = set()
    for i in found:
        dep.add(i.dept)
    return render(request, 'display.html', {'posts':found.order_by('dept','number'),'dept':dep,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'search': True,'school':request.user.profile.school.name})


def setting(request):
    (template, context) = authenticate(request.user)
    if template:
        return render(request, template, context)

    if request.method == 'POST':
        if 'username' in request.POST:
            if request.user.username == request.POST['username']:
                logout(request)
                User.objects.get(username=request.POST['username']).delete()
                return render(request, 'landing.html')
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

