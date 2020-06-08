from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()

class School(models.Model):
    name = models.TextField(blank=True)
    domain = models.TextField(unique=True)
    creator = models.TextField(blank=True)
    takedown = models.BooleanField(default=False)
    reason = models.TextField(default='')
    reviewed = models.BooleanField(default=False)
    def add_school(self,name,id):
        self.name = name
        self.creator = id
    def review(self):
        self.reviewed = True
    def topFive(self):
        return self.userprofile_set.annotate(submissions=Count('user__submission')).order_by('-submissions')[:5]


class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prof = models.TextField(blank=True)
    dept = models.TextField(blank=True)
    number = models.IntegerField(blank=True, validators=[MinValueValidator(0)])
    title = models.TextField(blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    semester = models.TextField(blank=True)
    hidden = models.BooleanField(default=True)
    year = models.TextField(blank=True)
    syllabus = models.FileField(blank=True, upload_to=settings.UPLOAD_TO)
    upvotes = models.IntegerField(default=1)
    def toggleHidden(self):
        self.hidden = not self.hidden



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    school = models.ForeignKey(School, null=True, on_delete=models.CASCADE)


class Suggestion(models.Model):
    name = models.TextField()
    suggestion_text = models.TextField()
    github_issue = models.TextField(default='')
    def __str__(self):
        return self.suggestion_text
