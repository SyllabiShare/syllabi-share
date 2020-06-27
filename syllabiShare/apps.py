from django.apps import AppConfig


class SyllabishareConfig(AppConfig):
    name = 'syllabiShare'

    def ready(self):
        import syllabiShare.signals  # noqa
