from django_summernote.apps import DjangoSummernoteConfig


class SummernoteConfig(DjangoSummernoteConfig):
    # Summernote's published migrations use AutoField for attachments.
    default_auto_field = 'django.db.models.AutoField'
