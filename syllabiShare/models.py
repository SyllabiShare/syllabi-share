from django.db import models
from jsonfield import JSONField

class Submission(models.Model):
    user = models.TextField()
    prof = models.TextField()
    course = models.TextField()
    school = models.TextField()
    syllabus = models.FileField(blank=True, upload_to='uploads/')
    upvotes = models.IntegerField(default = 1)

class School(models.Model):
    school = models.TextField(unique=True, blank=True)
    domain = models.TextField(unique=True)
    poster = models.TextField(blank=True)
    reviewed = models.BooleanField(default=False)
    uploads = JSONField(default={})
    def add_school(self,name,id):
        self.school = name
        self.poster = id
    def review(self):
        self.reviewed = True
    def upload(self,name):
        if name in self.uploads:
            self.uploads[name] += 1
        else:
            self.uploads[name] = 1
    def topFive(self,name):
        return [i for i in sorted(self.uploads.items(), key=lambda x: x[1], reverse=True)[:min(len(self.uploads),5)]]
        

class Suggestion(models.Model):
    name = models.TextField()
    suggestion_text = models.TextField()
    def __str__(self):
        return self.suggestion_text
