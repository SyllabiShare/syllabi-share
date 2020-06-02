from django.db import models
from jsonfield import JSONField
from django.conf import settings


class School(models.Model):
    name = models.TextField(blank=True)
    domain = models.TextField(unique=True)
    creator = models.TextField(blank=True)
    takedown = models.BooleanField(default=False)
    reason = models.TextField(default='')
    reviewed = models.BooleanField(default=False)
    uploads = JSONField(default={})
    def add_school(self,name,id):
        self.name = name
        self.creator = id
    def review(self):
        self.reviewed = True
    def upload(self,name):
        if name in self.uploads:
            self.uploads[name] += 1
        else:
            self.uploads[name] = 1
    def topFive(self):
        return [i for i in sorted(self.uploads.items(), key=lambda x: x[1], reverse=True)[:min(len(self.uploads),5)]]


class Submission(models.Model):
    user = models.TextField(blank=True)
    prof = models.TextField(blank=True)
    dept = models.TextField(blank=True)
    course = models.TextField(blank=True)
    title = models.TextField(blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    semester = models.TextField(blank=True)
    hidden = models.TextField(default=True)
    year = models.TextField(blank=True)
    syllabus = models.FileField(blank=True, upload_to=settings.UPLOAD_TO)
    upvotes = models.IntegerField(default = 1)


class Suggestion(models.Model):
    name = models.TextField()
    suggestion_text = models.TextField()
    github_issue = models.TextField(default='')
    def __str__(self):
        return self.suggestion_text
