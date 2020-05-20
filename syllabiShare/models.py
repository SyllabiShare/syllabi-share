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