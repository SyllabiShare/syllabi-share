from syllabiShare.models import UserProfile, School


def create_profile(backend, user, response, *args, **kwargs):
    start = user.email.index('@') + 1
    end = user.email.index('.edu')
    domain = user.email[start:end]
    profile = UserProfile(user=user, school=School.objects.get_or_create(domain=domain)[0])
    profile.save()
