from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from syllabiShare.models import UserProfile, School


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        start = instance.email.index('@') + 1
        end = instance.email.index('.edu')
        domain = instance.email[start:end]
        UserProfile.objects.create(user=instance, school=School.objects.get_or_create(domain=domain)[0])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
