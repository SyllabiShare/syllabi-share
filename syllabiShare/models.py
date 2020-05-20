from django.db import models

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
    def add_school(self,name,id):
        self.school = name
        self.poster = id
    def review(self):
        self.reviewed = True

class Suggestion(models.Model):
    name = models.TextField()
    suggestion_text = models.TextField()
    def __str__(self):
        return self.suggestion_text
