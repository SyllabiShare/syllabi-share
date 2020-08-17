from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mass_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View

from .forms import SignUpForm, ConfirmationEmailForm
from .models import Submission, School, Suggestion
from .tokens import account_activation_token


def takedown_check(user):
    return not user.profile.school.takedown


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
            messages.success(request, 'Your account has been confirmed.')
            return redirect('syllabiShare:index')
        else:
            # TODO: Throwing them back to the home page doesn't seem too helpful here.
            # They should have a way of regenerating an email.
            messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
            return redirect('syllabiShare:index')


class SignUpView(View):
    form_class = SignUpForm
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        # No signing up while logged in! Same for post()
        if request.user.is_authenticated:
            return redirect('syllabiShare:index')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('syllabiShare:index')
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your SyllabiShare Account'
            message = render_to_string('emails/account_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'confirm-account.html', {'host': settings.EMAIL_HOST_USER, 'email': user.email})
        return render(request, self.template_name, {'form': form, 'signup': True})


def confirm_account(request):
    if request.method == 'POST':
        email = request.POST['email']
        # Do not leak user account info -- always pretend we send an email, even if we don't
        try:
            user = User.objects.get(email=email)
            if not user.profile.email_confirmed:
                if user.profile.confirmations_sent < 3:
                    send_confirmation_email(user, request)
                else:
                    # ...unless they start spamming
                    return render(request, 'too-many-confirmations.html', {'email': settings.EMAIL_HOST_USER})
        except User.DoesNotExist:
            pass

        return redirect('resend_confirmation_done')
    else:
        if request.user.is_authenticated:
            return redirect('syllabiShare:index')

        return render(request, 'resend-confirmation-email.html', {'form': ConfirmationEmailForm()})


def confirm_account_done(request):
    if request.user.is_authenticated:
        return redirect('syllabiShare:index')

    return render(request, 'resend-done.html')


def send_confirmation_email(user, request):
    current_site = get_current_site(request)
    subject = 'Activate Your SyllabiShare Account'
    message = render_to_string('emails/account_confirmation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)

    user.profile.confirmations_sent += 1
    user.save()


def about(request):
    return render(request, 'about.html')


@login_required
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
    return redirect('syllabiShare:index')


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def display(request, dept=None):
    posts = Submission.objects.filter(school=request.user.profile.school).filter(dept=dept.upper()).filter(hidden=False).order_by('number')
    if not dept or len(posts) == 0:
        return redirect('/')
    return render(request, 'display.html', {'posts': posts, 'dept':dept,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN, 'school': request.user.profile.school.name})


# This one can't use the decorators because it needs to differentiate between landing & index
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'landing.html', {'form': SignUpForm()})

    if not takedown_check(request.user):
        return redirect('syllabiShare:takedown')

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
    return render(request, 'index.html', {'leaderboard':school.topFive(),'posts':sorted(list(dep)),'school':school.name,'num':len(posts), 'index':True})


def takedown(request):
    # Make sure this request is legit
    if request.user.is_authenticated and request.user.profile.school.takedown:
        return render(request, 'sorry.html',
                      {'reason': request.user.profile.school.reason,
                       'domain': request.user.email[request.user.email.index('@') + 1:]})

    # No? Redirect them to the index
    return redirect('syllabiShare:index')


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def myuploads(request):
    posts = Submission.objects.filter(school=request.user.profile.school).filter(user=request.user).order_by('dept', 'number')
    if len(posts) == 0:
        messages.error(request, 'You have not uploaded any syllabi yet.')
        return redirect('syllabiShare:upload') # nothing to show before uploading something!
    return render(request, 'myuploads.html', {'posts': posts, 'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN, 'school': request.user.profile.school.name, 'breadcrumb': 'Your Uploads'})


def privacy(request):
    return render(request, 'privacy.html', {'breadcrumb': 'Privacy Policy'})


@login_required
def schooladmin(request, domain=None):
    if request.user.is_superuser:
        try:
            school = School.objects.get(domain=domain)
        except:
            return redirect('syllabiShare:index')
        posts = Submission.objects.filter(school=school).filter(hidden=False)
        dep = set()
        for i in posts:
            dep.add(i.dept)
        return render(request, 'index.html', {'leaderboard':school.topFive(),'posts':sorted(list(dep)),'school':domain,'num':len(posts)})
    return redirect('syllabiShare:index')


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def search(request):
    found = Submission.objects.filter(school=request.user.profile.school).filter(hidden=False)
    if request.method == 'POST':
        if len(request.POST['search']) == 0:
            messages.error(request, "You didn't enter anything to search!")
            return redirect("syllabiShare:index")
        if 'save' in request.POST:
            request.user.profile.saved.add(Submission.objects.get(pk=request.POST['pk']))
        found = found.filter(prof__icontains=request.POST['search']) | found.filter(dept__icontains=request.POST['search']) | found.filter(title__icontains=request.POST['search'])
    dep = set()
    for i in found:
        dep.add(i.dept)
    return render(request, 'display.html', {'posts':found.order_by('dept', 'number'),'dept':dep,'AWS_S3_CUSTOM_DOMAIN':settings.AWS_S3_CUSTOM_DOMAIN,'search_string': request.POST['search'],'school':request.user.profile.school.name})


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def setting(request):
    if request.method == 'POST':
        if 'username' in request.POST:
            if request.user.username == request.POST['username']:
                logout(request)
                User.objects.get(username=request.POST['username']).delete()
                return redirect('syllabiShare:index')
    return render(request, 'settings.html',{ 'breadcrumb': 'Settings'})


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def suggest(request):
    if request.method == 'POST':
        suggestion = Suggestion()
        suggestion.name = request.user
        suggestion.suggestion_text = request.POST['suggestion']
        if 'githubLink' in request.POST and 'https://github.com/SyllabiShare/syllabi-share/issues/' in request.POST['githubLink']:
            suggestion.github_issue = request.POST['githubLink']
        suggestion.save()
        return redirect("syllabiShare:suggest")  # prevents re-post on refresh problem
    return render(request, 'suggest.html', {'suggestion':Suggestion.objects.all(), 'breadcrumb': 'Feedback'})


@login_required
@user_passes_test(takedown_check, login_url='syllabiShare:takedown', redirect_field_name=None)
def upload(request):
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
            messages.success(request, 'Syllabus successfully added. It will show up when we receive approval from the professor. Thank you!')
        else:
            messages.error(request, 'Please enter the professor\'s name as "FirstName LastName"')
        return redirect("syllabiShare:upload")  # prevents re-post on refresh problem
    return render(request, 'upload.html')


def view404(request, exception=None):
    return redirect('syllabiShare:index')

